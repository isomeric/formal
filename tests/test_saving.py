# hfoswarmongo
# ============
# Copyright 2015 riot <riot@hackerfleet.org> and others.
#
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

import warmongo


class TestCreating(unittest.TestCase):
    def setUp(self):
        self.schema = {
            'name': 'Country',
            "id": "#Country",
            'properties': {
                'name': {'type': 'string'},
                'abbreviation': {'type': 'string'},
                'languages': {
                    'type': ['array', 'null'],
                    'items': {
                        'type': 'string'
                    }
                }
            },
            'additionalProperties': False,
        }

        # Connect to warmongo_test - hopefully it doesn't exist
        warmongo.connect("warmongo_test")
        self.Country = warmongo.model_factory(self.schema)

        # Drop all the data in it
        self.Country.collection().remove({})

        # Create some defaults
        sweden = self.Country({
            "name": "Sweden",
            "abbreviation": "SE",
            "languages": ["swedish"]
        })

        sweden.save()

    def testNormalSave(self):
        """Test if saving goes well and does not create duplicates"""

        # Make sure there is only Sweden beforehand
        self.assertEqual(1, self.Country.count())

        sweden = self.Country.find_one({"abbreviation": "SE"})

        self.assertIsNotNone(sweden)
        self.assertEqual("Sweden", sweden.name)

        # Update Sweden and store it back
        sweden.name = "Sverige"
        sweden.validate()
        sweden.save()

        # Assert there still is only one Sweden
        self.assertEqual(1, self.Country.count())
        print(self.Country.count())

        # Get the updated entry and make sure it is good
        sverige = self.Country.find_one({"abbreviation": "SE"})

        self.assertEqual("Sverige", sverige.name)
        self.assertEqual("SE", sverige.abbreviation)
        self.assertEqual(1, len(sverige.languages))
        self.assertTrue("swedish" in sverige.languages)

    def testUpdate(self):
        """Test if saving goes well and does not create duplicates"""

        # Make sure there is only Sweden beforehand
        self.assertEqual(1, self.Country.count())

        sweden = self.Country.find_one({"abbreviation": "SE"})

        self.assertIsNotNone(sweden)
        self.assertEqual("Sweden", sweden.name)

        # Update Sweden and store it back
        sweden.update({'name': "Sverige", '_id': str(sweden._fields['_id'])})
        sweden.validate()
        sweden.save()

        # Assert there still is only one Sweden
        self.assertEqual(1, self.Country.count())
        print(self.Country.count())

        # Get the updated entry and make sure it is good
        sverige = self.Country.find_one({"abbreviation": "SE"})

        self.assertEqual("Sverige", sverige.name)
        self.assertEqual("SE", sverige.abbreviation)
        self.assertEqual(1, len(sverige.languages))
        self.assertTrue("swedish" in sverige.languages)
