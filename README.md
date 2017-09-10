[![Build Status](https://travis-ci.org/Hackerfleet/warmongo.svg)](https://travis-ci.org/Hackerfleet/warmongo)
# Warmongo!

This fork is being used for https://github.com/hackerfleet/hfos
We'll try to maintain upstream but will add certain features for the circuits framework, which we also use:
https://bitbucket.org/circuits/circuits

Things that have changed:
* jsonschema is now truly used to validate objects (it validates far more than just basetypes)
* we do ignore mongo's object_id - not sure if this is a good thing, but it helps with the schemata
* we require (by spec) an 'id' field that lists a uri for the schema
* the resulting field is enforced on instantiated objects, too, so clients can validate by schema-id

## Description

This is a package for generating classes from a JSON-schema that are to be
saved in MongoDB and (un)pickled via Python's builtin json module or others like simplejson or ujson.

This extends the JSON schema by supporting extra BSON types:
* ObjectId - use the `"object_id"` type in your JSON schema to validate that
             a field is a valid ObjectId.
* datetime - use the `"date"` type in your JSON schema to validate that a field
             is a valid datetime

## Usage

1) Build your schema

    >>> schema = {
        'name': 'Country',
        'id': '#country',
        'properties': {
            'name': {'type': 'string'},
            'abbreviation': {'type': 'string'},
        },
        'additionalProperties': False,
    }

2) Connect to your database

    >>> import warmongo
    >>> warmongo.connect("test")

3) Create a model

    >>> Country = warmongo.model_factory(schema)

4) Create an object using your model

    >>> sweden = Country({"name": 'Sweden', "abbreviation": 'SE'})
    >>> sweden.save()
    >>> sweden._id
    ObjectId('50b506916ee7d81d42ca2190')

5) Let the object validate itself!

    >>> sweden = Country.find_one({"name" : "Sweden"})
    >>> sweden.name = 5
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "warmongo/model.py", line 254, in __setattr__
        self.validate_field(attr, self._schema["properties"][attr], value)
      File "warmongo/model.py", line 189, in validate_field
        self.validate_simple(key, value_schema, value)
      File "warmongo/model.py", line 236, in validate_simple
        (key, value_type, str(value), type(value)))
    warmongo.exceptions.ValidationError: Field 'name' is of type 'string', received '5' (<type 'int'>)

    >>> sweden.overlord = 'Bears'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "warmongo/model.py", line 257, in __setattr__
        raise ValidationError("Additional property '%s' not allowed!" % attr)
    warmongo.exceptions.ValidationError: Additional property 'overlord' not allowed!

6) You can also update objects from dictionaries:

    >>> sweden.update({"name": "Sverige"})
    >>> sweden.save()

7) To get them to a browser or other similar things, serialize them:

    >>> sweden.serializablefields()
    {'_id': '50b506916ee7d81d42ca2190', 'name': 'Sverige', 'abbreviation': 'SE', 'id': '#country'}


## Choosing a collection

By default Warmongo will use the pluralized version of the model's name. If
you want to use something else, put it in the JSON-schema:

    {
        "name": "MyModel",
        ...
        "collectionName": "some_collection",
        ...
    }

## Multiple Databases

To use multiple databases, simply call `connect()` multiple times:

    >>> import warmongo
    >>> warmongo.connect("test")
    >>> warmongo.connect("other_db")

By default all models will use the first database specified. If you want to use
a different one, put it in the JSON-schema:

    {
        "name": "MyModel",
        ...
        "databaseName": "other_db",
        ...
    }

## PostgreSQL as backend

Please see https://www.torodb.com/stampede/docs/1.0.0-beta3/quickstart/ on how to set up ToroDB Stampede. 

## Licence

Apache Version 2.0

## Change notice

This file has been changed by the Hackerfleet Community and a change notice has
been added to all modified files in accordance to the Apache License 2.0

## Production Examples

The Hackerfleet uses warmongo as ORM system to deal with data objects in a developer and enduser friendly way.
See it in action on http://github.com/hackerfleet/hfos

The original author uses warmongo every day at his startup http://www.sweetiq.com/ to share data
definitions between their Python and Node.js applications. It has been running in
production for some time now, so it has been reasonably tested for robustness
and performance.
