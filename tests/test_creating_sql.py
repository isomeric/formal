#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Formal
# ======
#
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
Test SQL support. WiP!
"""

import unittest

import formal


class TestCreatingSQL(unittest.TestCase):
    def setUp(self):
        """Set up the test scaffolding"""
        self.schema = {
            'name': 'Country',
            'sql': True,
            'id': '#Country',
            'properties': {
                'name': {'type': 'string'},
                'abbreviation': {'type': 'string', 'primary': True},
                'dialcode': {'type': 'integer'}
            },
            'additionalProperties': False,
        }

        formal.connect_sql(":memory:", 'sqlite', '', '', '', 0)

        self.Country = formal.model_factory(self.schema)

        # Drop all the data in it
        # self.Country.clear()

        # Create some defaults
        self.Country({
            "name": "Sweden",
            "abbreviation": "SE",
            "dialcode": 46
        }).save()
        self.Country({
            "name": "United States of America",
            "abbreviation": "US",
            "dialcode": 1
        }).save()

    def testNormalCreateSQL(self):
        """ Test with doing things the SQL way """

        canada = self.Country({
            "name": "Canada",
            "abbreviation": "CA",
            "dialcode": 1
        })

        canada.save()

        country = self.Country.find({'dialcode': 1}, skip=1)

        from pprint import pprint
        for item in country:
            pprint(item.serializablefields())

        # canada.delete()

        self.assertEqual("Canada", canada.name)
        self.assertEqual("CA", canada.abbreviation)
        self.assertEqual(1, canada.dialcode)
