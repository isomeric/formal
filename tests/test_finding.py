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


class TestFinding(unittest.TestCase):
    def setUp(self):
        """Set up the test scaffolding"""
        self.schema = {
            'name': 'Country',
            "id": "#Country",
            'properties': {
                'name': {'type': 'string'},
                'abbreviation': {'type': 'string'},
                'languages': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                }
            },
            'additionalProperties': False,
        }

        # Connect to formal_test - hopefully it doesn't exist
        formal.connect("formal_test")
        self.Country = formal.model_factory(self.schema)

        # Drop all the data in it
        self.Country.collection().delete_many({})

        # Create some defaults
        sweden = self.Country({
            "name": "Sweden",
            "abbreviation": "SE",
            "languages": ["swedish"]
        })
        sweden.save()
        usa = self.Country({
            "name": "United States of America",
            "abbreviation": "US",
            "languages": ["english"]
        })
        usa.save()

    def testFindOne(self):
        """ Test grabbing a single value the Mongo way """

        usa = self.Country.find_one({"abbreviation": "US"})

        self.assertIsNotNone(usa)
        self.assertEqual("United States of America", usa.name)

    def testFind(self):
        """ Just grab a bunch of stuff """

        countries = self.Country.find()

        # Since find() returns a generator, need to convert to list
        countries = [c for c in countries]

        self.assertEqual(2, len(countries))

    def testCount(self):
        """ See if everything is there """
        self.assertEqual(2, self.Country.count())
        self.assertEqual(1, self.Country.count({"abbreviation": "SE"}))
        self.assertEqual(0, self.Country.count({"abbreviation": "CA"}))

    def testFindAll(self):
        """ Test fetching everything the mongo way """

        countries = self.Country.find({"abbreviation": "SE"})

        # Since find() returns a generator, need to convert to list
        countries = [c for c in countries]

        self.assertEqual(1, len(countries))
        self.assertEqual("Sweden", countries[0].name)
