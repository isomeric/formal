from warlock.model import Model as WarlockModel
import database

import inflect, re

from bson import ObjectId

inflect_engine = inflect.engine()

class Model(WarlockModel):
    def __init__(self, schema, *args, **kwargs):
        if len(kwargs) == 0 and len(args) > 0:
            # creating object with first element in args as object
            kwargs = args[0]
            args = args[1:]

        # creating object in kwargs form
        WarlockModel.__init__(self, schema, *args, **self.from_mongo(kwargs))

    def save(self):
        d = dict(self)

        self._id = str(self.collection().save(self.to_mongo(d)))

    ''' Retrieve an element from the database. If it doesn't exist, create it. '''
    @classmethod
    def find_or_create(cls, *args, **kwargs):
        result = cls.find_one(*args, **kwargs)

        if result == None:
            result = cls(*args, **kwargs)

        return result

    ''' Grabs a set of elements from the DB.
    Note: This returns a generator, so you can't to do an efficient count. To get a count
    '''
    @classmethod
    def find(cls, *args, **kwargs):
        if len(kwargs) > 0 and len(args) == 0:
            # Allow find to accept kwargs format for querying, pass things
            # to pymongo as it expects
            args = (kwargs,) + args
            kwargs = {}

        result = cls.collection().find(*args, **kwargs)

        for obj in result:
            yield cls(**obj)

    @classmethod
    def find_one(cls, *args, **kwargs):
        if len(kwargs) > 0 and len(args) == 0:
            # Allow find_one to accept kwargs format for querying, pass things
            # to pymongo as it expects
            args = (kwargs,) + args
            kwargs = {}

        result = cls.collection().find_one(*args, **kwargs)
        if result != None:
            return cls(**result)
        return None

    ''' Counts the number of items:
        - not the same as pymongo's count, this is the equivalent to:
            collection.find(*args, **kwargs).count()
    '''
    @classmethod
    def count(cls, *args, **kwargs):
        if len(kwargs) > 0 and len(args) == 0:
            # Allow find to accept kwargs format for querying, pass things
            # to pymongo as it expects
            args = (kwargs,) + args
            kwargs = {}

        return cls.collection().find(*args, **kwargs).count()

    @classmethod
    def collection(cls):
        return database.get_collection(collection=cls.collection_name())

    @classmethod
    def collection_name(cls):
        global inflect_engine
        return inflect_engine.plural(cls.__name__.lower())

    def from_mongo(self, d):
        ''' Convert a dict from Mongo format to our format. '''
        for k, v in d.items():
            if isinstance(v, ObjectId):
                d[k] = str(v)
            elif isinstance(v, dict):
                d[k] = self.from_mongo(v)

        return d

    def to_mongo(self, d):
        ''' Convert a dict to Mongo format from our format. '''
        id_re = re.compile('^[a-f0-9]{24}$')

        # convention: if a field ends in _id and matches a 24-digit hex number,
        # convert it to an ObjectId
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = self.to_mongo(v)
            elif k.endswith("_id") and id_re.match(v):
                d[k] = ObjectId(v)

        return d
