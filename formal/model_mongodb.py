#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Formal
# ======
#
# Copyright 2013 Rob Britton
# Copyright 2015-2019 Heiko 'riot' Weinen <riot@c-base.org> and others.
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
Changes notice
==============

This file has been changed by the Hackerfleet Community and this notice has
been added in accordance to the Apache License 2.0

"""

from bson import ObjectId
from pymongo import DESCENDING

from .model_base import ModelBase
import formal.database
from .exceptions import InvalidReloadException

from copy import copy


class Model(ModelBase):
    """The Mongodb object model class"""

    def reload(self):
        """ Reload this object's data from the DB. """
        result = self.__class__.find_by_id(self._id)

        # result will be None in the case that this object hasn't yet been
        # saved to the DB, or if the object has been deleted since it was
        # fetched
        if result:
            self._fields = self.cast(result._fields)
        else:
            raise InvalidReloadException("No object in the database with ID %s" % self._id)

    def save(self, *args, **kwargs):
        """ Saves an object to the database. """
        self.validate()

        self._fields['_id'] = self.collection().save(self._fields, *args,
                                                            **kwargs)

    def delete(self):
        """ Removes an object from the database. """
        try:
            self.collection().delete_one({
                "_id": ObjectId(str(self._fields[
                                        '_id']))
            })
        except Exception as e:
            print("Uh oh: ", e, type(e))

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
        docs = [obj._fields for obj in objects]
        return cls.collection().insert(docs)

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
        Note: This returns a generator, so you can't to do an efficient count.
        To get a count, use the count() function which accepts the same
        arguments as find() with the exception of non-query fields like sort,
        limit, skip.
        """
        options = {}

        for option in ["sort", "limit", "skip", "batch_size"]:
            if option in kwargs:
                options[option] = kwargs[option]
                del options[option]

        if "batch_size" in options and "skip" not in options and "limit" not in options:
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
            result = cls.collection().find(*args, **kwargs)

            if "sort" in options:
                result = result.sort(options["sort"])

            if "skip" in options:
                result = result.skip(options["skip"])

            if "limit" in options:
                result = result.limit(options["limit"])

            for obj in result:
                yield cls(obj, from_find=True)

    @classmethod
    def find_by_id(cls, obj_id, **kwargs):
        """ Finds a single object from this collection. """

        if isinstance(obj_id, str):
            obj_id = ObjectId(obj_id)

        args = {"_id": obj_id}

        result = cls.collection().find_one(args, **kwargs)
        if result is not None:
            return cls(result, from_find=True)
        return None

    @classmethod
    def find_latest(cls, *args, **kwargs):
        """ Finds the latest one by _id and returns it. """
        kwargs["limit"] = 1
        kwargs["sort"] = [("_id", DESCENDING)]

        result = cls.collection().find(*args, **kwargs)

        if result.count() > 0:
            return cls(result[0], from_find=True)
        return None

    @classmethod
    def find_one(cls, *args, **kwargs):
        """ Finds a single object from this collection. """
        result = cls.collection().find_one(*args, **kwargs)
        if result is not None:
            return cls(result)
        return None

    @classmethod
    def count(cls, object_filter=None):
        """ Counts the number of items:
            - not the same as pymongo's count, this is the equivalent to:
                collection.find(*args, **kwargs).count()
        """
        if object_filter is None:
            object_filter = {}

        # TODO: WTF. Yeah. I love deprecation warnings, too, pymongo.
        if hasattr(cls.collection, 'count_documents'):
            return cls.collection().count_documents(object_filter)
        else:
            return cls.collection().count(object_filter)

    @classmethod
    def collection(cls):
        """ Get the pymongo collection object for this model. Useful for
        features not supported by formal like aggregate queries and
        map-reduce. """
        return formal.database.get_collection(collection=cls.collection_name(),
                                              database=cls.database_name())
