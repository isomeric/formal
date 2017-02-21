# hfoswarmongo
# ============
# Copyright 2013 Rob Britton
# Copyright 2015 riot <riot@hackerfleet.org> and others.
#
# This file has been changed and this notice has been added in
# accordance to the Apache License
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

from datetime import datetime

import re
from copy import deepcopy
from bson import ObjectId
from jsonschema import validate, Draft4Validator, validators
from jsonschema.exceptions import ValidationError
from bson.errors import InvalidId
from .exceptions import InvalidSchemaException

class OutdatedCodeException(Exception):
    pass


ValidTypes = {
    "integer": int,
    "boolean": bool,
    "number": float,
    "string": str,
    "object_id": ObjectId,
    "date": datetime
}

def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            #print(property, subschema)
            if "default" in subschema:
                #print("Setting default: ", subschema['default'])
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )


DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)


class ModelBase(object):
    """ This class serves as a base class for the main model types in
    warmongo: Model, and TwistedModel. """

    def __init__(self, fields={}, from_find=False, *args, **kwargs):
        """ Creates an instance of the object."""
        self._from_find = from_find

        fields = deepcopy(fields)

        # populate any default fields for objects that haven't come from the DB
        if not from_find:
            DefaultValidatingDraft4Validator(self._schema).validate(fields)
            #for field, details in self._schema["properties"].items():
            #    if "default" in details and not field in fields:
            #        fields[field] = details["default"]

        self._fields = self.cast(fields)
        self.validate()

    def get(self, field, default=None):
        """ Get a field if it exists, otherwise return the default. """
        return self._fields.get(field, default)

    @classmethod
    def collection_name(cls):
        """ Get the collection associated with this class. The convention is
        to take the lowercase of the class name and pluralize it. """
        if cls._schema.get("collectionName"):
            return cls._schema.get("collectionName")
        elif cls._schema.get("name"):
            name = cls._schema.get("name")
        else:
            name = cls.__name__

        # convert to snake case
        name = (name[0] + re.sub('([A-Z])', r'_\1', name[1:])).lower()

        return name

    @classmethod
    def database_name(cls):
        """ Get the database associated with this class. Meant to be overridden
        in subclasses. """
        if cls._schema.get("databaseName"):
            return cls._schema.get("databaseName")
        return None

    def to_dict(self):
        """ Convert the object to a dict. """
        return self._fields

    def validate(self):
        """ Validate `schema` against a dict `obj`. """
        #self.validate_field("", self._schema, self._fields)
        try:
            pass
            # TODO: Deepcopying for validation is probably not so good ;)
            fields = dict(self._fields)
            if '_id' in fields:
                try:
                    obj_id = ObjectId(fields['_id'])
                except InvalidId:
                    raise ValidationError('Invalid object ID: ', fields['_id'])

                # Now remove for schema validation (jsonschema knows nothing off object ids)
                del (fields['_id'])

            validate(fields, self._schema)
        except ValidationError as e:
            raise ValidationError("Error:\n" + str(e) + "\nFields:\n" + str(self._fields))


    def cast(self, fields, schema=None):
        """ Cast the fields from Mongo into our format - necessary to convert
        floats into ints since Javascript doesn't support ints. """
        if schema is None:
            schema = self._schema

        value_type = schema.get("type", "object")

        if value_type == "object" and isinstance(fields, dict) and \
                schema.get("properties"):
            result = dict()
            for key, value in fields.items():
                result[key] = self.cast(value, schema["properties"].get(key, {}))
            return result
        elif value_type == "array" and isinstance(fields, list) and schema.get("items"):
            return [
                self.cast(value, schema["items"]) for value in fields
            ]
        elif value_type == "integer" and isinstance(fields, float):
            # The only thing that needs to be casted: floats -> ints
            return int(fields)
        elif value_type == "object_id":
            return str(fields)
        else:
            return fields

    def __str__(self):
        return str(self.to_dict())

    def __getattr__(self, attr):
        """ Get an attribute from the fields we've selected. Note that if the
        field doesn't exist, this will return None. """
        if attr in self._schema["properties"] and attr in self._fields:
            return self._fields.get(attr)
        else:
            raise AttributeError("Item has no attribute '%s'" % attr)


        # if attr.startswith('_'):
        #     return super(ModelBase, self).__getattr__(attr)
        #
        # if attr in self._schema["properties"] and attr in self._fields:
        #     #print("Direct hit")
        #     return self._fields.get(attr)
        # curschema = self._schema["properties"]
        # curfields = self._fields
        # path = attr
        # newattr = path
        #
        # #print("Query path:", path)
        # #print("Initial Fields:", curfields)
        #
        # while '.' in path:
        #
        #     newattr, path = path.split('.', maxsplit=1)
        #     #print("Looking for intermediate path in ", newattr, path)
        #
        #     if newattr in curschema and newattr in curfields:
        #         curschema = curschema[newattr]['properties']
        #         curfields = curfields[newattr]
        #     else:
        #         raise AttributeError("Item has no intermediate attribute '%s'"
        #                              % ( newattr))
        #
        #
        # if newattr in curschema and newattr in curfields:
        #     return curfields.get(newattr)
        # else:
        #     raise AttributeError("Item has no attribute '%s'" % ( attr))

    def __setattr__(self, attr, value):
        """ Set one of the fields, with validation. Exception is on "private"
        fields - the ones that start with _. """
        if attr.startswith("_"):
            if attr == '_id':
                try:
                    self._fields['_id'] = ObjectId(value)
                except InvalidId:
                    raise ValidationError("Invalid ObjectId")
            return object.__setattr__(self, attr, value)

        if attr in self._schema["properties"]:
            # Check the field against our schema
            validator = deepcopy(self)
            validator._fields[attr] = value
            validator.validate()
        elif not self._schema.get("additionalProperties", True):
            # not allowed to add additional properties
            raise ValidationError("Additional property '%s' not allowed!" % attr)

        self._fields[attr] = value
        return value

    def update(self, newfields, updateId=False):
        try:
            for key, value in newfields.items():
                if not key == "_id" or updateId:
                    self.__setattr__(key, value)
        except Exception as e:
            raise ValidationError("Unknown Validation error: '%s' (%s)" % (e, type(e)))
