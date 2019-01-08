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

from .model_mongodb import Model as formalModel
from .model_sqlalchemy import Model as SQLModel
from .exceptions import InvalidSchemaException

from copy import deepcopy
from .database import connect, connect_sql
import pymongo

# Export connect so we can do formal.connect()
connect = connect
connect_sql = connect_sql

# Export some constants from pymongo
ASCENDING = pymongo.ASCENDING
DESCENDING = pymongo.DESCENDING


def model_factory(schema, base_class=formalModel):
    """ Construct a model based on `schema` that inherits from `base_class`."""

    if not schema.get("id"):
        raise InvalidSchemaException("No id field in schema!")

    if not schema.get("properties"):
        raise InvalidSchemaException("No properties field in schema!")

    if not schema.get("name"):
        raise InvalidSchemaException(
            "formal models require a top-level 'name' attribute!")

    if schema.get('sql', False):
        print("SQL Schema detected!")
        base_class = SQLModel

        from .database import sql_database
        engine = sql_database
        primary = None
        for item in schema['properties']:
            thing = schema['properties'][item].get('primary', False)
            if thing is not False:
                assert primary is None
                primary = item
    else:
        engine = None
        primary = None

    schema = deepcopy(schema)

    class Model(base_class):
        """Factory for the model"""

        _schema = schema
        _engine = engine
        _primary = primary

        def __init__(self, *args, **kwargs):
            self._schema = schema
            self._engine = engine
            self._primary = primary

            base_class.__init__(self, *args, **kwargs)

    Model.__name__ = str(schema["name"])

    return Model
