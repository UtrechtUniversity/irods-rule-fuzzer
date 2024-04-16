"""A fuzzer for iRODS rules"""

import argparse
from collections import OrderedDict
import random
import time
import sys
import uuid

from irods_rule_fuzzer.endpoint_discovery.csv_import import CSVImportEndpointDiscovery
from irods_rule_fuzzer.input_generator.random_generator import RandomInputGenerator
from irods_rule_fuzzer.rule import call_rule
from irods_rule_fuzzer.session import setup_session


def _get_args():
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-ssl', action='store_true', default=False,
                        help='Do not use SSL/TLS when connecting to iRODS')
    parser.add_argument('--sleep-time', type=int, default=0,
                        help='time to sleep between rule invocations, in milliseconds')
    parser.add_argument('--ca-file', default="/etc/ssl/certs/localhost_and_chain.crt",
                        help="Certificate authority file for validating iRODS server certificate")
    parser.add_argument("csvfile", help="CSV file with endpoints to test")
    return parser.parse_args()


def entry():
    args = _get_args()
    session = setup_session(use_ssl=not args.no_ssl, ca_file=args.ca_file)
    endpoint_discovery = CSVImportEndpointDiscovery(args.csvfile)
    endpoints = endpoint_discovery.discover_endpoints()
    input_generator = RandomInputGenerator()
    while True:
        endpoint = random.choice(endpoints)
        marker = str(uuid.uuid4())
        call_fuzzmarker(session, marker + ":begin")
        arguments = input_generator.generate_input(endpoint)
        n_output_params = endpoint["Number of output parameters"]
        print(marker + ":" + endpoint["Endpoint name"] + " " + str(arguments))
        try:
            call_rule(session, endpoint["Endpoint name"], arguments, n_output_params, endpoint["Rule engine"])
        except Exception as e:
            print("Unexpected exception occurred: " + str(e))
        call_fuzzmarker(session, marker + ":end")
        if args.sleep_time > 0:
            time.sleep(args.sleep_time)


def call_fuzzmarker(session, marker):
    """Calls fuzz marker function as a bookmark to relate log messages to fuzzing actions.
       This function also servers as a check to see if iRODS is still responding."""
    parms = OrderedDict([
        ('logmarker', marker)])
    [out] = call_rule(session, 'fuzzCheck', parms, 1, "irods_rule_engine_plugin-irods_rule_language-instance")
    if out != "OK":
        print("Fuzzing rule not okay. Terminating.")
        sys.exit(1)
