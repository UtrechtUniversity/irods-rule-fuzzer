"""Endpoint discovery by importing endpoint data from a CSV file
   The CSV file should have three columns:
   1. Endpoint name
   2. Number of input parameters
   3. Number of output parameters
   4. Rule engine

   If an endpoint can have different numbers of arguments, or run on different
   rule engines, it should be split across multiple lines.
"""
import csv


class CSVImportEndpointDiscovery:

    def __init__(self, inputfile):
        self.inputfile = inputfile

    def discover_endpoints(self):
        result = []
        with open(self.inputfile) as inputfile:
            for row in csv.DictReader(inputfile):
                out = {}
                out["Endpoint name"] = row["Endpoint name"]
                out["Number of input parameters"] = int(row["Number of input parameters"])
                out["Number of output parameters"] = int(row["Number of output parameters"])
                out["Rule engine"] = row["Rule engine"]
                result.append(out)
        return result
