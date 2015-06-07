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
