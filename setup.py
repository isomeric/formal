"""
Changes notice
==============

This file has been changed by the Hackerfleet Community and this notice has
been added in accordance to the Apache License 2.0

The original author's data is:
 author='Rob Britton',
 author_email='rob@robbritton.com',
 url='http://github.com/robbrit/warmongo',
"""

import setuptools

setuptools.setup(
    name="hfos-warmongo",
    version="0.5.5",
    description="JSON-Schema-based ORM for MongoDB",
    author="Heiko 'riot' Weinen",
    author_email="riot@hackerfleet.org",
    url="http://github.com/Hackerfleet/hfos-warmongo",
    keywords=["mongodb", "jsonschema"],
    packages=["warmongo"],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Front-Ends"
    ],
    long_description="""\
  JSON-Schema-based ORM for MongoDB
  ---------------------------------

  Allows you to build models validated against a JSON-schema file, and save
  them to MongoDB.
""",
    install_requires=["pymongo>=3.2",
                      "jsonschema>=2.6.0",
                      ],
    test_suite="tests"
)
