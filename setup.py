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

This file has been changed by the Hackerfleet and Isomeric Communities and this notice has
been added in accordance to the Apache License 2.0

The original author's data is:
 author='Rob Britton',
 author_email='rob@robbritton.com',
 url='http://github.com/robbrit/formal',
"""

import setuptools

setuptools.setup(
    name="formal",
    description="JSON-Schema-based ORM for MongoDB and SQLAlchemy",
    author="Heiko 'riot' Weinen",
    author_email="riot@c-base.org",
    url="http://github.com/isomeric/formal",
    keywords=["mongodb", "sqlalchemy", "jsonschema", "orm"],
    packages=["formal"],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Front-Ends"
    ],
    long_description="""\
JSON-Schema-based ODM for MongoDB and SQL
-----------------------------------------

Allows you to build models validated against a JSON-schema file, and save
them to MongoDB or SQL based databases.
""",
    install_requires=[
        "pymongo>=3.2",
        "jsonschema==2.6.0",
        "deepdiff>=3.2.1",
        "sqlalchemy>=1.2.14"
    ],
    test_suite="tests",
    use_scm_version={
        "write_to": "formal/scm_version.py",
    },
    setup_requires=[
        "setuptools_scm"
    ],
)
