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

import unittest
from bson import ObjectId

import formal
# from formal.exceptions import ValidationError
from jsonschema.exceptions import ValidationError


class TestValidation(unittest.TestCase):
    def testValidateArray(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "field": ["asdf", "hello"]
        })

        self.assertEqual(2, len(m.field))
        self.assertEqual("asdf", m.field[0])
        self.assertRaises(ValidationError, model, {
            "field": "hi"
        })

    def testValidateString(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "string"
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "field": "asdf"
        })

        self.assertEqual("asdf", m.field)
        self.assertRaises(ValidationError, model, {
            "field": 5
        })

    def testValidateObject(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "object",
                    "properties": {
                        "subfield": {"type": "string"}
                    }
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "field": {"subfield": "asdf"}
        })

        self.assertEqual("asdf", m.field["subfield"])
        self.assertRaises(ValidationError, model, {
            "field": "hi"
        })

    def testValidateNumber(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "number"
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "field": 5.5
        })

        self.assertEqual(5.5, m.field)
        self.assertRaises(ValidationError, model, {
            "field": "hi"
        })

        # using an int should still work
        m = model({
            "field": 5
        })

        self.assertEqual(5, m.field)

    def testValidateMany(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": ["string", "null"]
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "field": "asdf"
        })

        self.assertEqual("asdf", m.field)
        self.assertRaises(ValidationError, model, {
            "field": 5
        })

        m.field = None

        self.assertIsNone(m.field)

    def testValidateObjectId(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "_id": {
                    "type": "string",
                    "pattern": "^(?=[a-f\d]{24}$)(\d+[a-f]|[a-f]+\d)",
                    "additionalProperties": False
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "_id": str(ObjectId("45cbc4a0e4123f6920000002"))
        })

        self.assertEqual(ObjectId("45cbc4a0e4123f6920000002"), ObjectId(m._id))
        self.assertRaises(ValidationError, model, {
            "_id": "hi"
        })

    def testValidateInteger(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "integer"
                }
            }
        }

        model = formal.model_factory(schema)

        self.assertRaises(ValidationError, model, {
            "field": "hi"
        })

    def testValidateBool(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "boolean"
                }
            }
        }

        model = formal.model_factory(schema)

        m = model({
            "field": False
        })

        self.assertEqual(False, m.field)
        self.assertRaises(ValidationError, model, {
            "field": "hi"
        })
