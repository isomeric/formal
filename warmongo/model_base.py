# Copyright 2013 Rob Britton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import inflect
from copy import deepcopy
from bson import ObjectId
from datetime import datetime

from exceptions import ValidationError, InvalidSchemaException

inflect_engine = inflect.engine()

ValidTypes = {
    "integer": int,
    "boolean": bool,
    "number": float,
    "string": basestring,
    "object_id": ObjectId,
    "date": datetime
}


class ModelBase(object):
    ''' This class serves as a base class for the main model types in
    warmongo: Model, and TwistedModel. '''

    def __init__(self, fields={}, from_find=False, *args, **kwargs):
        ''' Creates an instance of the object.'''
        self._from_find = from_find

        fields = deepcopy(fields)

        # populate any default fields for objects that haven't come from the DB
        if not from_find:
            for field, details in self._schema["properties"].items():
                if "default" in details and not field in fields:
                    fields[field] = details["default"]

        self._fields = self.cast(fields)
        self.validate()

    def get(self, field, default=None):
        ''' Get a field if it exists, otherwise return the default. '''
        return self._fields.get(field, default)

    @classmethod
    def collection_name(cls):
        ''' Get the collection associated with this class. The convention is
        to take the lowercase of the class name and pluralize it. '''
        global inflect_engine
        if cls._schema.get("collectionName"):
            return cls._schema.get("collectionName")
        elif cls._schema.get("name"):
            name = cls._schema.get("name")
        else:
            name = cls.__name__

        # convert to snake case
        name = (name[0] + re.sub('([A-Z])', r'_\1', name[1:])).lower()

        # pluralize
        return inflect_engine.plural(name)

    @classmethod
    def database_name(cls):
        ''' Get the database associated with this class. Meant to be overridden
        in subclasses. '''
        if cls._schema.get("databaseName"):
            return cls._schema.get("databaseName")
        return None

    def to_dict(self):
        ''' Convert the object to a dict. '''
        return self._fields

    def validate(self):
        ''' Validate `schema` against a dict `obj`. '''
        self.validate_field("", self._schema, self._fields)

    def validate_field_type(self, key, value_schema, value, value_type):
        if isinstance(value_type, list):
            for subtype in value_type:
                try:
                    self.validate_field_type(key, value_schema, value, subtype)
                    # We got this far, so break
                    break
                except ValidationError:
                    # Ignore it
                    pass
            else:
                # None of them passed,
                raise ValidationError("Field '%s' must be one of the following types: '%s', received '%s' (%s)" %
                                      (key, ", ".join(value_type), str(value), type(value)))
        elif value_type == "array":
            self.validate_array(key, value_schema, value)
        elif value_type == "object":
            self.validate_object(key, value_schema, value)
        elif value_type == "null":
            self.validate_null(key, value_schema, value)
        else:
            self.validate_simple(key, value_type, value)

    def validate_field(self, key, value_schema, value):
        ''' Validate a single field in `value` named `key` against `value_schema`. '''
        # check the type
        value_type = value_schema.get("type", "object")

        self.validate_field_type(key, value_schema, value, value_type)

    def validate_array(self, key, value_schema, value):
        if not isinstance(value, list):
            raise ValidationError("Field '%s' is of type 'array', received '%s' (%s)" %
                                  (key, str(value), type(value)))

        if value_schema.get("items"):
            for item in value:
                self.validate_field(key, value_schema["items"], item)
        else:
            # no items, this is an untyped array
            pass

    def validate_object(self, key, value_schema, value):
        if not isinstance(value, dict):
            raise ValidationError("Field '%s' is of type 'object', received '%s' (%s)" %
                                  (key, str(value), type(value)))

        if not value_schema.get("properties"):
            # no validation on this object
            return

        for subkey, subvalue in value_schema["properties"].items():
            if subkey in value:
                self.validate_field(subkey, subvalue, value[subkey])
            elif subvalue.get("required", False) and not self._from_find:
                # if the field is required and we haven't pulled from find,
                # throw an exception
                raise ValidationError("Field '%s' is required but not found!" %
                                        subkey)

        # Check for additional properties
        if not value_schema.get("additionalProperties", True):
            extra = set(value.keys()) - set(value_schema["properties"].keys())

            if len(extra) > 0:
                raise ValidationError("Additional properties are not allowed: %s" %
                                        ', '.join(list(extra)))

    def validate_null(self, key, value_schema, value):
        if value is not None:
            raise ValidationError("Field '%s' is expected to be null!" % key)

    def validate_simple(self, key, value_type, value):
        ''' Validate a simple field (not an object or array) against a schema. '''
        if value_type == "any":
            # can be anything
            pass
        elif value_type == "number" or value_type == "integer":
            # special case: can be an int or a float
            valid_types = [int, float, long]
            matches = [klass for klass in valid_types if isinstance(value, klass)]

            print matches

            if len(matches) == 0:
                raise ValidationError("Field '%s' is of type '%s', received '%s' (%s)" %
                                      (key, value_type, str(value), type(value)))
        elif value_type in ValidTypes:
            if not isinstance(value, ValidTypes[value_type]):
                raise ValidationError("Field '%s' is of type '%s', received '%s' (%s)" %
                                      (key, value_type, str(value), type(value)))
            # TODO: check other things like maximum, etc.
        else:
            # unknown type
            raise InvalidSchemaException("Unknown type '%s'!" % value_type)

    def cast(self, fields, schema=None):
        ''' Cast the fields from Mongo into our format - necessary to convert
        floats into ints since Javascript doesn't support ints. '''
        if schema is None:
            schema = self._schema

        value_type = schema.get("type", "object")

        if value_type == "object" and isinstance(fields, dict) and schema.get("properties"):
            return {
                key: self.cast(value, schema["properties"].get(key, {})) for key, value in fields.items()
            }
        elif value_type == "array" and isinstance(fields, list) and schema.get("items"):
            return [
                self.cast(value, schema["items"]) for value in fields
            ]
        elif value_type == "integer" and isinstance(fields, float):
            # The only thing that needs to be casted: floats -> ints
            return int(fields)
        else:
            return fields

    def __getattr__(self, attr):
        ''' Get an attribute from the fields we've selected. Note that if the
        field doesn't exist, this will return None. '''
        if attr in self._schema["properties"] and attr in self._fields:
            return self._fields.get(attr)
        else:
            raise AttributeError("%s has no attribute '%s'" % (str(self), attr))

    def __setattr__(self, attr, value):
        ''' Set one of the fields, with validation. Exception is on "private"
        fields - the ones that start with _. '''
        if attr.startswith("_"):
            return object.__setattr__(self, attr, value)

        if attr in self._schema["properties"]:
            # Check the field against our schema
            self.validate_field(attr, self._schema["properties"][attr], value)
        elif not self._schema.get("additionalProperties", True):
            # not allowed to add additional properties
            raise ValidationError("Additional property '%s' not allowed!" % attr)

        self._fields[attr] = value
        return value
