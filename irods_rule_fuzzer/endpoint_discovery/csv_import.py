"""Endpoint discovery by importing endpoint data from a CSV file
   The CSV file should have six columns:
   1. Endpoint name
   2. Endpoint type ("regular_legacy", "regular_python", "yoda_api" )
   3. Number of parameters. Only for type regular_python
   4. Number of input parameters. Only for type regular_legacy.
   5. Number of output parameters. Only for type regular_legacy
   6. Input parameter names, slash delimited, e.g. ("collection/object"). Only for type yoda_api

   Meaning of recognized types:
  - regular_legacy: a rule written in the legacy rule language. Can also be used for microservices.
  - regular_python: a rule written in Python
  - yoda_api: a Python rule with a Yoda api.make annotation. These results should receive one
    parameter with JSON-encoded parameter values.
"""
import csv
import sys


class CSVImportEndpointDiscovery:

    def __init__(self, inputfile):
        self.inputfile = inputfile

    def discover_endpoints(self):
        result = []
        choice_fields = {"Endpoint type": ["regular_legacy", "regular_python", "yoda_api"]}
        str_fields = ["Endpoint name", "Endpoint type"]
        int_fields = ["Number of parameters", "Number of input parameters", "Number of output parameters"]
        list_fields = ["Input parameter names"]
        with open(self.inputfile) as inputfile:
            for row in csv.DictReader(inputfile):
                out = {}
                for field in str_fields:
                    out[field] = row[field]
                for field in int_fields:
                    out[field] = int(row[field]) if len(row[field]) > 0 else 0
                for field in list_fields:
                    out[field] = row[field].split("/") if len(row[field]) > 0 else []
                for fields in choice_fields.items():
                    if row[fields[0]] in fields[1]:
                        out[fields[0]] = row[fields[0]]
                    else:
                        print("Error: " + row[fields[0]] + " is not a valid type of " + fields[0])
                        sys.exit(1)

                result.append(out)
        return result
