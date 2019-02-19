#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Formal
# ======
#
# Copyright 2018-2019 Heiko 'riot' Weinen <riot@c-base.org> and others.
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
#

"""
SQL Support for Formal
"""

import re
import sqlalchemy as sql
from deepdiff import DeepDiff
from .model_base import DefaultValidatingDraft4Validator
from .database import sql_database
from jsonschema import validate, Draft4Validator, validators
from jsonschema.exceptions import ValidationError
from copy import copy, deepcopy

from pprint import pprint


class Model(object):
    """The SQL object model class"""

    def __init__(self, original_fields=None, from_find=False, *args, **kwargs):
        """ Creates an instance of the object."""
        if original_fields is None:
            original_fields = {}
            
        self._from_find = from_find

        metadata = sql.MetaData()

        self._table = sql.Table(self._schema['name'], metadata)
        for item, value in self._schema['properties'].items():
            # print(item)
            column_type = value['type'].upper()
            primary = value.get('primary', False)

            if primary:
                self._primary = item

            column = sql.String(64)

            if column_type == 'INTEGER':
                column = sql.Integer
            elif column_type == 'STRING':
                length = value.get('length', 64)
                column = sql.String(length)

            self._table.append_column(sql.Column(item, column, primary_key=primary))

        from .database import sql_database
        metadata.create_all(sql_database)

        self._engine = sql_database

        fields = deepcopy(original_fields)
        has_id = False
        if '_id' in fields:
            has_id = True
            del fields['_id']

        # populate any default fields for objects that haven't come from the DB
        if not from_find:
            DefaultValidatingDraft4Validator(self._schema).validate(fields)
            # for field, details in self._schema["properties"].items():
            #    if "default" in details and not field in fields:
            #        fields[field] = details["default"]

        self._fields = self.cast(fields)
        self.validate()
        if has_id:
            self._fields['_id'] = original_fields['_id']

    def reload(self):
        """ Reload this object's data from the DB. """
        pass

    def save(self, *args, **kwargs):
        """ Saves an object to the database. """
        self.validate()

        #print(**self._fields)
        insert = self._table.insert().values(**self._fields)
        result = self._engine.execute(insert)
        return result.inserted_primary_key

    def delete(self):
        """ Removes an object from the database. """

        primary = self._fields[self._primary]

        query = "DELETE FROM {table_name} WHERE {table_name}.{primary_key} = {primary}".format(**{
            'table_name': self._schema['name'],
            'primary_key': self._primary,
            'primary': primary
        })

        delete = sql.text(query)
        result = self._engine.execute(delete)
        return result

    def serializablefields(self):
        """Return serializable fields of the object"""
        result = copy(self._fields)

        result['id'] = self._schema['id']

        if '_id' in result:
            result['_id'] = str(result['_id'])

        return result

    @classmethod
    def bulk_create(cls, objects, *args, **kwargs):
        """ Create a number of objects (yay performance). """
        print("WARNING! NOT IMPLEMENTED: BULK_CREATE")
        pass
        # return cls.collection().insert(docs)

    @classmethod
    def find_or_create(cls, query, *args, **kwargs):
        """ Retrieve an element from the database. If it doesn't exist, create
        it.  Calling this method is equivalent to calling find_one and then
        creating an object. Note that this method is not atomic.  """
        result = cls.find_one(query, *args, **kwargs)

        if result is None:
            default = cls._schema.get("default", {})
            default.update(query)

            result = cls(default, *args, **kwargs)

        return result

    @classmethod
    def find(cls, *args, **kwargs):
        """ Grabs a set of elements from the DB.
        Note: This returns a generator, so you can't do an efficient count.
        To get a count, use the count() function which accepts the same
        arguments as find() with the exception of non-query fields like sort,
        limit, skip.
        """
        options = {}

        for option in ["sort", "limit", "skip", "batch_size"]:
            if option in kwargs:
                options[option] = kwargs[option]
                del options[option]

        if "batch_size" in options and "skip" not in options and "limit" not \
                in options:
            # run things in batches
            current_skip = 0
            limit = options["batch_size"]

            found_something = True

            while found_something:
                found_something = False

                result = cls.collection().find(*args, **kwargs)
                result = result.skip(current_skip).limit(limit)

                if "sort" in options:
                    result = result.sort(options["sort"])

                for obj in result:
                    found_something = True
                    yield cls(obj, from_find=True)

                current_skip += limit
        else:
            result = cls._find(*args, **kwargs)

            if "sort" in options:
                result = result.sort(options["sort"])

            if "skip" in options:
                result = result.skip(options["skip"])

            if "limit" in options:
                result = result.limit(options["limit"])

            for sql_thing in result.fetchall():
                obj = cls._transform_object(sql_thing)
                yield cls(obj, from_find=True)

    @classmethod
    def _transform_object(cls, thing):
        return dict(zip(cls._schema['properties'], thing))

    @classmethod
    def find_by_id(cls, obj_id, **kwargs):
        """ Finds a single object from this collection. """

        if isinstance(obj_id, str):
            obj_id = obj_id

        args = {"_id": obj_id}

        result = cls.collection().find_one(args, **kwargs)
        if result is not None:
            return cls(result, from_find=True)
        return None

    @classmethod
    def find_latest(cls, *args, **kwargs):
        """ Finds the latest one by _id and returns it. """
        kwargs["limit"] = 1
        kwargs["sort"] = (cls._primary, "DESC")

        result = cls._find(*args, **kwargs)

        # if result.count() > 0:
        #    return cls(result[0], from_find=True)
        return result.fetchone()

    @classmethod
    def _find(cls, *args, **kwargs):
        # pprint(args)
        # pprint(kwargs)
        limit = kwargs.get('limit', False)
        sort = kwargs.get('sort', False)

        name = cls._schema['name']
        # print('Yeeaaah, i\'m building a query right now... it might not have a', name)

        query = "SELECT %s FROM %s" % (",".join(cls._schema['properties'].keys()), name)

        if len(args) > 0 and not args[0] == {}:
            query += " WHERE"
            # pprint(args)

        for item in args:
            for key, value in item.items():
                if isinstance(value, str):
                    value = "'%s'" % value
                query += " %s.%s = %s AND" % (name, key, value)

        query = query.rstrip(' AND')

        if sort is not False:
            query += " ORDER BY %s %s" % (sort[0], sort[1])
        if limit is not False:
            query += " LIMIT %i" % limit

        find = sql.text(query)
        result = cls._engine.execute(find)
        return result

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Finds a single object from this collection."""

        result = cls._find(*args, **kwargs).fetchone()
        # pprint(result)
        if result is not None:
            return cls(result)
        return None

    @classmethod
    def count(cls, *args, **kwargs):
        """ Counts the number of items:

        """
        name = cls._schema['name']

        query = "SELECT COUNT(*) FROM %s" % name
        proxy = cls._engine.execute(query).scalar()

        return int(proxy)

    @classmethod
    def clear(cls):
        """Clear a collection"""

        query = "DELETE FROM {table_name}".format(**{
            'table_name': cls._schema['name'],
        })

        clear = sql.text(query)
        result = cls._engine.execute(clear)
        return result

    @classmethod
    def collection(cls):
        """ Get the pymongo collection object for this model. Useful for
        features not supported by formal like aggregate queries and
        map-reduce. """

        return None
        # return formal.database.get_collection(
        #    collection=cls.collection_name(),
        #    database=cls.database_name())

    @classmethod
    def make_migration(cls, new_schema):
        """Make migrations for a schema"""

        delta = DeepDiff(cls._schema, new_schema)
        return delta

    @classmethod
    def migrate(cls, patchset):
        """Migrate an object model with a patchset"""

        def apply_patch(patch):
            """Apply a patch to all objects of a model"""

            def migrate_thing(migration_thing, migration_patch):
                """Apply all diffs in a patch to an object"""

                for diff in migration_patch:
                    print('Would now apply ', diff, migration_patch[diff], 'to',
                          migration_thing.name)

            for thing in cls.collection().find_all():
                migrate_thing(thing, patch)

        for key in patchset:
            print('Applying patch', key)
            apply_patch(patchset[key])

    ###################################################################################################################

    def get(self, field, default=None):
        """ Get a field if it exists, otherwise return the default. """
        return self._fields.get(field, default)

    @classmethod
    def collection_name(cls):
        """ Get the collection associated with this class. """
        name = cls._schema.get(
            "collectionName",
            cls._schema.get(
                "collectionName",
                cls._schema.get("name",
                                cls.__name__)
            )
        )

        # convert to snake case
        name = (name[0] + re.sub('([A-Z])', r'_\1', name[1:])).lower()

        return name

    @classmethod
    def database_name(cls):
        """ Get the database associated with this class. Meant to be overridden
        in subclasses. """
        return cls._schema.get("databaseName", None)

    def to_dict(self):
        """ Convert the object to a dict. """
        return self._fields

    def validate(self):
        """ Validate `schema` against a dict `obj`. """
        # self.validate_field("", self._schema, self._fields)
        try:
            pass
            # TODO: Deep-copying for validation is probably not so good ;)
            fields = dict(self._fields)
            if '_id' in fields:
                # Now remove for schema validation (jsonschema knows nothing
                #  off object ids)
                del (fields['_id'])

            validate(fields, self._schema)
        except ValidationError as e:
            raise ValidationError(
                "Error:\n" + str(e) + "\nFields:\n" + str(self._fields))

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
                result[key] = self.cast(value,
                                        schema["properties"].get(key, {}))
            return result
        elif value_type == "array" and isinstance(fields, list) and schema.get(
                "items"):
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
        """Return string representation of this object model"""
        return str(self.to_dict())

    def __repr__(self):
        """Return a representation for debugging purposes"""
        return str(self.name if self.name is not None else self.to_dict())

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
            # current_schema = self._schema["properties"]
            # current_fields = self._fields
            # path = attr
            # new_attribute = path
            #
            # #print("Query path:", path)
            # #print("Initial Fields:", current_fields)
            #
            # while '.' in path:
            #
            #     new_attribute, path = path.split('.', maxsplit=1)
            #     #print("Looking for intermediate path in ", new_attribute, path)
            #
            #     if new_attribute in current_schema and new_attribute in current_fields:
            #         current_schema = current_schema[new_attribute]['properties']
            #         current_fields = current_fields[new_attribute]
            #     else:
        #         raise AttributeError("Item has no intermediate attribute '%s'"
        #                              % ( new_attribute))
        #
        #
        # if new_attribute in current_schema and new_attribute in current_fields:
        #     return current_fields.get(new_attribute)
        # else:
        #     raise AttributeError("Item has no attribute '%s'" % ( attr))

    def __setattr__(self, attr, value):
        """ Set one of the fields, with validation. Exception is on "private"
        fields - the ones that start with _. """
        if attr.startswith("_"):
            return object.__setattr__(self, attr, value)

        if attr in self._schema["properties"]:
            # Check the field against our schema
            original = self._fields[attr]
            self._fields[attr] = value

            try:
                self.validate()
            except ValidationError as e:
                self._fields[attr] = original
                raise e

        elif not self._schema.get("additionalProperties", True):
            # not allowed to add additional properties
            raise ValidationError(
                "Additional property '%s' not allowed!" % attr)

        self._fields[attr] = value
        return value

    def update(self, new_fields, update_id=False):
        """Update an object's fields"""

        #try:
        if True:
            for key, value in new_fields.items():
                if not key == "_id" or update_id:
                    self.__setattr__(key, value)
        #except Exception as e:
        #    raise ValidationError(
        #        "Unknown Validation error: '%s' (%s)" % (e, type(e)))
