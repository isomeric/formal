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

import unittest
from datetime import datetime
from bson import ObjectId

import warmongo
#from warmongo.exceptions import ValidationError
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "field": ["asdf", "hello"]
        })

        self.assertEqual(2, len(m.field))
        self.assertEqual("asdf", m.field[0])
        self.assertRaises(ValidationError, Model, {
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "field": "asdf"
        })

        self.assertEqual("asdf", m.field)
        self.assertRaises(ValidationError, Model, {
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "field": {"subfield": "asdf"}
        })

        self.assertEqual("asdf", m.field["subfield"])
        self.assertRaises(ValidationError, Model, {
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "field": 5.5
        })

        self.assertEqual(5.5, m.field)
        self.assertRaises(ValidationError, Model, {
            "field": "hi"
        })

        # using an int should still work
        m = Model({
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "field": "asdf"
        })

        self.assertEqual("asdf", m.field)
        self.assertRaises(ValidationError, Model, {
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "_id": str(ObjectId("45cbc4a0e4123f6920000002"))
        })

        self.assertEqual(ObjectId("45cbc4a0e4123f6920000002"), ObjectId(m._id))
        self.assertRaises(ValidationError, Model, {
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

        Model = warmongo.model_factory(schema)

        # floats should not cause validation errors, but they do get truncated
        m = Model({
            "field": 7.8
        })

        self.assertEqual(7, m.field)
        self.assertRaises(ValidationError, Model, {
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

        Model = warmongo.model_factory(schema)

        m = Model({
            "field": False
        })

        self.assertEqual(False, m.field)
        self.assertRaises(ValidationError, Model, {
            "field": "hi"
        })
