# irods-rule-fuzzer
An experimental fuzzer for iRODS rules

This tool tests the robustness of iRODS rules by invoking them
repeatedly with random input values.

## Requirements

This tool is intended to be used with Python 3.8 or newer, and iRODS 4.2.12 or newer.

## Installation

First install the irods-rule-checker in a Python 3 virtual environment.

For example:

```
python3 -m venv venv
python3 -m pip install --upgrade ./irods-rule-fuzzer
```

Ensure that the rule included in `fuzz.r` has been added to the ruleset of
the iRODS zone you are testing. This rule is used to add bookmarks to the rodsLog
so that it is easier to relate error messages to rule invocations. This rule
also serves as a keepalive check.

## Usage

```
usage: irods-rule-fuzzer [-h] [--no-ssl] [--sleep-time SLEEP_TIME] [--ca-file CA_FILE] csvfile

A fuzzer for iRODS rules

positional arguments:
  csvfile               CSV file with endpoints to test

optional arguments:
  -h, --help            show this help message and exit
  --no-ssl              Do not use SSL/TLS when connecting to iRODS
  --sleep-time SLEEP_TIME
                        time to sleep between rule invocations, in milliseconds
  --ca-file CA_FILE     Certificate authority file for validating iRODS server certificate
```

The CSV file should contain a list of endpoints (e.g. rules, microservices to test).

It should have the following columns:
1. Endpoint name
2. Number of input parameters
3. Number of output parameters
4. Rule engine

An example is provided in `examples/example-rule-file-yoda.csv`.
