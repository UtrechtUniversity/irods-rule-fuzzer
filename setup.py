from setuptools import setup

setup(
    author="Sietse Snel",
    author_email="s.t.snel@uu.nl",
    description=('A rule-based fuzzer for testing iRODS rules'),
    install_requires=[
        'python-irodsclient==2.0.0',
    ],
    name='irods_rule_fuzzer',
    packages=['irods_rule_fuzzer',
              'irods_rule_fuzzer.endpoint_discovery',
              'irods_rule_fuzzer.input_generator',
              'irods_rule_fuzzer.input_translator'],
    entry_points={
        'console_scripts': [
            'irods-rule-fuzzer = irods_rule_fuzzer:entry',
        ]
    },
    version='0.0.1'
)
