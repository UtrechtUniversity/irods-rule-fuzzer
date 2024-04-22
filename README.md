# irods-rule-fuzzer
An experimental fuzzer for iRODS rules

This tool tests the robustness of iRODS rules by invoking them
repeatedly with random input values. It is meant to be used on test and development environments.

## Requirements

This tool is intended to be used with Python 3.8 or newer, and iRODS 4.2.12 or newer.

## Installation

First install the irods-rule-checker in a Python 3 virtual environment.

For example:

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install wheel
python3 -m pip install --upgrade ./irods-rule-fuzzer
```

Ensure that the rule included in `uuFuzz.r` has been added to the ruleset of
the iRODS zone you are testing. This rule is used to add bookmarks to the rodsLog
so that it is easier to relate error messages to rule invocations. This rule
also serves as a keepalive check.

## Usage

Simple example to test a few example rules in Yoda:

```
irods-rule-fuzzer --print-output --endpoint-csv-file examples/example-regular-legacy.csv
```

```
usage: irods-rule-fuzzer [-h] [--no-ssl] [--print-output]
                         [--sleep-time SLEEP_TIME] [--ca-file CA_FILE]
                         [--yoda-ruleset-dir YODA_RULESET_DIR]
                         [--endpoint-csv-file ENDPOINT_CSV_FILE]

A fuzzer for iRODS rules

optional arguments:
  -h, --help            show this help message and exit
  --no-ssl              Do not use SSL/TLS when connecting to iRODS
  --print-output        Print output of rules
  --sleep-time SLEEP_TIME
                        time to sleep between rule invocations, in
                        milliseconds
  --ca-file CA_FILE     Certificate authority file for validating iRODS server
                        certificate
  --yoda-ruleset-dir YODA_RULESET_DIR
                        Directory with Yoda ruleset to extract endpoints from
  --endpoint-csv-file ENDPOINT_CSV_FILE
                        CSV file with endpoints to test
```

At a high level, the fuzzer works as follows:
1. First, it discovers endpoints (rules and microservices) that can be executed.
   See below for details.
2. The fuzzer than enters a loop, in which it randomly selects an endpoint and
   invokes it with random input values. The results are stored in the rodsLog

The user can then search the rodsLog for any unexpected problems that occurred
when rules were invoked with random data (e.g. segfaults, uncaught exceptions, SQL errors).

## Endpoint discovery

Endpoints (rules and microservices) can currently be discovered in two ways: (1) by
extracting them from a Yoda ruleset, and (2) by reading a list of endpoints provided
by a user in a CSV file. It is also possible to use both methods.

### CSV import

The CSV file should have six columns:
   1. Endpoint name
   2. Endpoint type (`regular_legacy`, `regular_python`, `yoda_api`)
   3. Number of parameters. Only for type regular_python
   4. Number of input parameters. Only for type regular_legacy.
   5. Number of output parameters. Only for type regular_legacy
   6. Input parameter names, slash delimited, e.g. ("collection/object"). Only for type yoda_api

Meaning of recognized types:
- `regular_legacy`: a rule written in the legacy rule language. Can also be used for microservices.
- `regular_python`: a rule written in Python
- `yoda_api`: a Python rule with a Yoda api.make annotation. These results should receive one
parameter with JSON-encoded parameter values.

Please find examples of endpoint CSV files in the CSV directory.

### Yoda ruleset extraction

The fuzzer can also extract rules from the ruleset:
1. For Python rules, functions with an `api.make` or `rule.make` annotation are extracted. These
   decorators are used for most Python Yoda rules.
2. For legacy rule language rules, text patterns are used to extract rule names and the number of
   arguments. A process of trial-and-error is used to determine which arguments are input arguments.

Note that this process does not find all endpoints. For examples, microservices are not discovered, as
well as rules that do not use the standard decorators. These need to be supplied using another method
(e.g. CSV import)

## Tips and tricks

* Consider disabling cronjobs that invoke iRODS rules on the system, in order to reduce the
  number of log messages that are not related to fuzzing.
