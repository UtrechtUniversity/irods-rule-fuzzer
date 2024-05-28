"""A fuzzer for iRODS rules"""

import argparse
from collections import OrderedDict
import logging
import random
import time
import sys
import uuid

from irods.exception import NO_RULE_OR_MSI_FUNCTION_FOUND_ERR

from irods_rule_fuzzer.endpoint_discovery.csv_import import CSVImportEndpointDiscovery
from irods_rule_fuzzer.endpoint_discovery.yoda_ruleset import YodaRulesetEndpointDiscovery
from irods_rule_fuzzer.input_generator.random_generator import RandomInputGenerator
from irods_rule_fuzzer.input_translator.yoda_api_translator import YodaAPIInputTranslator
from irods_rule_fuzzer.rule import call_rule
from irods_rule_fuzzer.session import setup_session


def _get_args():
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-ssl', action='store_true', default=False,
                        help='Do not use SSL/TLS when connecting to iRODS')
    parser.add_argument('--print-output', action='store_true', default=False,
                        help='Print output of rules')
    parser.add_argument('--sleep-time', type=int, default=0,
                        help='time to sleep between rule invocations, in milliseconds')
    parser.add_argument('--ca-file', default="/etc/ssl/certs/localhost_and_chain.crt",
                        help="Certificate authority file for validating iRODS server certificate")
    parser.add_argument('--yoda-ruleset-dir', default=None, required=False,
                        help="Directory with Yoda ruleset to extract endpoints from")
    parser.add_argument("--endpoint-csv-file", default=None, required=False,
                        help="CSV file with endpoints to test")
    parser.add_argument("-v", "--verbose", action='store_true', default=False,
                        help="Print information about fuzzing actions.")

    args = parser.parse_args()

    if args.yoda_ruleset_dir is None and args.endpoint_csv_file is None:
        print("Error: you need to provide an endpoint CSV file and/or a Yoda ruleset directory")
        sys.exit(1)

    return args


def collect_endpoints(args):
    endpoints = []
    if args.endpoint_csv_file is not None:
        csv_endpoint_discovery = CSVImportEndpointDiscovery(args.endpoint_csv_file)
        endpoints.extend(csv_endpoint_discovery.discover_endpoints())
    if args.yoda_ruleset_dir is not None:
        yoda_endpoint_discovery = YodaRulesetEndpointDiscovery(args.yoda_ruleset_dir)
        endpoints.extend(yoda_endpoint_discovery.discover_endpoints())
    return endpoints


def entry():
    setup_logger()
    try:
        main(_get_args())
    except KeyboardInterrupt:
        print("Script interrupted by user.", file=sys.stderr)


def setup_logger():
    logging.basicConfig()
    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    new_handler = logging.StreamHandler()
    new_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    root_logger.addHandler(new_handler)

    root_logger.setLevel(logging.INFO)


def main(args):
    session = setup_session(use_ssl=not args.no_ssl, ca_file=args.ca_file)
    endpoints = collect_endpoints(args)

    if len(endpoints) == 0:
        print("Error: no endpoints found.")
        sys.exit(1)
    elif args.verbose:
        logging.info("Endpoint discovery finished.")

    try:
        call_fuzzmarker(session, "Fuzzer starting...", verbose=args.verbose)
    except NO_RULE_OR_MSI_FUNCTION_FOUND_ERR:
        print("Error: The fuzzCheck rule was not found. It needs to be installed in order to run the fuzzer.\n"
              + "See README.md for details.")
        sys.exit(1)

    endpoints_with_extra_data = guess_missing_endpoint_parameters(session, endpoints, args)

    input_generator = RandomInputGenerator()
    yoda_api_translator = YodaAPIInputTranslator()
    while True:
        fuzz_data = {}
        fuzz_data["Endpoint"] = random.choice(endpoints_with_extra_data)
        fuzz_data["Marker"]  = str(uuid.uuid4())
        fuzz_data["Initial arguments"] = input_generator.generate_input(fuzz_data["Endpoint"])

        if fuzz_data["Endpoint"]["Endpoint type"] == "yoda_api":
            fuzz_data["Arguments"] = yoda_api_translator.translate_input(
                fuzz_data["Endpoint"],
                fuzz_data["Initial arguments"])
        else:
            fuzz_data["Arguments"] = fuzz_data["Initial arguments"]

        call_fuzzmarker(session,
                        fuzz_data["Marker"] + ":begin",
                        verbose=args.verbose)

        call_fuzzmarker(session,
                        fuzz_data["Marker"] + ":"
                        + fuzz_data["Endpoint"]["Endpoint name"] + " called with arguments"
                        + str(fuzz_data["Initial arguments"]),
                        verbose=args.verbose)
        try:
            result = None
            if fuzz_data["Endpoint"]["Endpoint type"] == "regular_python":
                result = call_rule(session,
                                   fuzz_data["Endpoint"]["Endpoint name"],
                                   fuzz_data["Arguments"],
                                   None,
                                   "irods_rule_engine_plugin-irods_rule_language-instance")
            elif fuzz_data["Endpoint"]["Endpoint type"] == "regular_legacy":
                result = call_rule(session,
                                   fuzz_data["Endpoint"]["Endpoint name"],
                                   fuzz_data["Arguments"],
                                   fuzz_data["Endpoint"]["Number of output parameters"],
                                   "irods_rule_engine_plugin-irods_rule_language-instance")
            elif fuzz_data["Endpoint"]["Endpoint type"] == "yoda_api":
                result = call_rule(session,
                                   fuzz_data["Endpoint"]["Endpoint name"],
                                   fuzz_data["Arguments"],
                                   None,
                                   "irods_rule_engine_plugin-irods_rule_language-instance")
            else:
                print("Unknown endpoint type: " + fuzz_data["Endpoint"]["Endpoint type"])

        except Exception as e:
            short_description = str(get_irods_exception_code(e))
            long_description = get_irods_exception_description(e)
            call_fuzzmarker(session,
                            fuzz_data["Marker"] + ":Exception occurred: " + short_description,
                            verbose=args.verbose)
            if args.print_output or args.verbose:
                print("Exception information: " + long_description)

        if result is not None:
            result_str = output_arguments_to_str(fuzz_data["Endpoint"]["Endpoint type"], result)
            call_fuzzmarker(session,
                            fuzz_data["Marker"] + "Rule output: " + result_str,
                            verbose=args.verbose)
            if args.print_output:
                endpoint_name = fuzz_data["Endpoint"]["Endpoint name"]
                str_arguments = str(fuzz_data["Initial arguments"])
                print(f"Rule output for {endpoint_name}({str_arguments}): {result_str}")

        call_fuzzmarker(session,
                        fuzz_data["Marker"] + ":end",
                        verbose=args.verbose)
        if args.sleep_time > 0:
            time.sleep(args.sleep_time)


def get_irods_exception_description(e):
    return str(type(e)) + ":" + str(e)


def get_irods_exception_code(e):
    if type(e) is KeyError:
        return str(e)
    else:
        try:
            return e.code
        except KeyError:
            return None


def output_arguments_to_str(endpoint_type, arguments):
    if endpoint_type == "regular_python":
        # The last return value of Python rules is zero bytes. Ignore them.
        return str(arguments[:-1])
    elif endpoint_type == "yoda_api":
        # API endpoints return results as 1 JSON string
        return str(arguments[0])
    else:
        return str(arguments)


def guess_missing_endpoint_parameters(session, endpoints_in, args):
    endpoints_out = []
    call_fuzzmarker(session, "Parameter discovery starting")
    for endpoint in endpoints_in:
        if (endpoint["Endpoint type"] == "regular_legacy"
            and "Number of input parameters" not in endpoint
                and "Number of output parameters" not in endpoint):
            endpoint_name = endpoint["Endpoint name"]
            endpoint_out = endpoint.copy()
            number_of_parameters = endpoint["Number of parameters"]
            call_fuzzmarker(session,
                            f"Parameter discovery for endpoint {endpoint_name} starting.",
                            verbose=args.verbose)
            for number_of_output_parameters in range(number_of_parameters + 1):
                input_parameters = []
                number_of_input_parameters = number_of_parameters - number_of_output_parameters
                for n in reversed(list(range(0, number_of_input_parameters))):
                    input_parameters.append(("param" + str(n), "param_num_test"))
                try:
                    parser_error = False
                    call_rule(session,
                              endpoint_name,
                              OrderedDict(input_parameters),
                              number_of_output_parameters,
                              "irods_rule_engine_plugin-irods_rule_language-instance")
                except Exception as e:
                    exception_code = get_irods_exception_code(e)
                    if exception_code in ("-1201000", "-1211000", "-1234000"):
                        parser_error = True
                discovery_message = f"Parameter discovery for {endpoint_name} " + \
                                    f"({str(number_of_input_parameters)} input and " + \
                                    f"{str(number_of_output_parameters)} output param(s)) :" + \
                                    (" failed " if parser_error else " succeeded")
                call_fuzzmarker(session,
                                discovery_message,
                                verbose=args.verbose)
                if not parser_error:
                    endpoint_out["Number of input parameters"] = number_of_input_parameters
                    endpoint_out["Number of output parameters"] = number_of_output_parameters
                    endpoints_out.append(endpoint_out)
                    break
            call_fuzzmarker(session,
                            f"Parameter discovery for endpoint {endpoint_name} finished.",
                            verbose=args.verbose)
        else:
            endpoints_out.append(endpoint)
    call_fuzzmarker(session,
                    "Parameter discovery ended.",
                    verbose=args.verbose)
    return endpoints_out


def call_fuzzmarker(session, marker, verbose=False):
    """Calls fuzz marker function as a bookmark to relate log messages to fuzzing actions.
       This function also servers as a check to see if iRODS is still responding."""
    parms = OrderedDict([
        ('logmarker', marker)])
    if verbose:
        logging.info(marker)
    [out] = call_rule(session, 'fuzzCheck', parms, 1, "irods_rule_engine_plugin-irods_rule_language-instance")
    if out != "OK":
        print("Fuzzing rule not okay. Terminating.")
        sys.exit(1)
