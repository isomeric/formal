import setuptools

setuptools.setup(
    name='warmongo',
    version='0.5.4-hf',
    description='JSON-Schema-based ORM for MongoDB',
    author='Rob Britton',
    author_email='rob@robbritton.com',
    url='http://github.com/robbrit/warmongo',
    keywords=["mongodb", "jsonschema"],
    packages=['warmongo'],
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
    install_requires=['pymongo==3.0.1',
                      'jsonschema==2.5.0',
                      ],
    test_requires=['nose',
                   'coverage'],
    test_suite="tests"
)
