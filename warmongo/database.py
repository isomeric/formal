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
#

''' Interface to pymongo '''

import pymongo


class NotConnected(RuntimeError):
    pass

# List of all the databases we have connected to
connections = {}

# List of databases
databases = {}

# The first connection we make is the default database
default_database = None


def connect(database, username=None, password=None, host="localhost", port=27017):
    ''' Connect to a database. '''
    global default_database

    identifier = (host, port)

    connection = connections.get(identifier)

    if connection is None:
        connection = pymongo.MongoClient(host, port)

    connections[identifier] = connection

    if not database in databases:
        db = connection[database]

        if username is not None and password is not None:
            db.authenticate(username, password)

        databases[database] = db

        if default_database is None:
            default_database = db


def get_database(database=None):
    ''' Get a database by name, or the default database. '''
    global default_database

    # Check default
    if database is None:
        if default_database is None:
            raise NotConnected("no connection to the database has been made.")
        else:
            return default_database
    try:
        return databases[database]
    except KeyError:
        raise NotConnected("connect() hasn't been called on '%s'" % database)


def get_collection(collection, database=None):
    return get_database(database)[collection]
