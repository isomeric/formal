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

import formal


class TestValidation(unittest.TestCase):
    def testCastWithObject(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "object",
                    "properties": {
                        "subfield": {"type": "integer"}
                    }
                }
            }
        }
        model = formal.model_factory(schema)

        m = model()

        old_fields = {
            "field": {
                "subfield": 5.2
            }
        }

        fields = m.cast(old_fields)

        self.assertEqual(5, fields["field"]["subfield"])

    def testCastWithArray(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                }
            }
        }
        model = formal.model_factory(schema)

        m = model()

        old_fields = {
            "field": [5.2, 7]
        }

        fields = m.cast(old_fields)

        self.assertEqual(5, fields["field"][0])
        self.assertEqual(7, fields["field"][1])

    def testBasicCast(self):
        schema = {
            "name": "Model",
            "id": "#Model",
            "properties": {
                "field": {"type": "integer"},
                "other_field": {"type": "string"},
            }
        }
        model = formal.model_factory(schema)

        m = model()

        old_fields = {
            "field": 5.2,
            "other_field": "5"
        }

        fields = m.cast(old_fields)

        self.assertEqual(5, fields["field"])
        self.assertEqual("5", fields["other_field"])
