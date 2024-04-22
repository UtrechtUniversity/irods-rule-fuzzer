"""This endpoint discovery class discovers Yoda rules by examining the
   Yoda ruleset in the following way:
   1. It parses all Python files in the apex directory, and extracts functions
      that have a @rule.make or @api.make decorator. This covers most (though not all)
      Yoda rules
   2. It scans legacy rule files in the apex directory, and extracts rule
      names using text patterns. Since the rule files are not parsed, this is an
      approximation.


"""

import ast
from glob import glob
import re


class YodaRulesetEndpointDiscovery:

    def __init__(self, ruleset_directory):
        self.ruleset_directory = ruleset_directory

    def discover_endpoints(self):
        endpoints = []
        endpoints.extend(self._discover_legacy_rule_language_endpoints())
        endpoints.extend(self._discover_python_endpoints())
        return endpoints

    def _discover_legacy_rule_language_endpoints(self):
        endpoints = []
        for filename in glob(self.ruleset_directory + "/*.r"):
            endpoints.extend(self._discover_legacy_rule_language_endpoints_in_file(filename))
        return endpoints

    def _discover_python_endpoints(self):
        endpoints = []
        for filename in glob(self.ruleset_directory + "/*.py"):
            endpoints.extend(self._discover_python_endpoints_in_file(filename))
        return endpoints

    def _discover_python_endpoints_in_file(self, filename):
        with open(filename, 'r') as file:
            source_code = file.read()

        tree = ast.parse(source_code)

        class RuleFinder(ast.NodeVisitor):
            def __init__(self):
                self.endpoints = []

            def visit_FunctionDef(self, node):
                function_name = node.name
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        decorator = decorator.func.value.id + "." + decorator.func.attr
                        function_name = node.name
                        arg_names = [arg.arg for arg in node.args.args][1:]
                        if decorator == "api.make":
                            self.endpoints.append({"Endpoint name": function_name,
                                                   "Endpoint type": "yoda_api",
                                                   "Number of parameters": len(arg_names),
                                                   "Parameter names": arg_names})
                        elif decorator == "rule.make":
                            self.endpoints.append({"Endpoint name": function_name,
                                                   "Endpoint type": "regular_python",
                                                   "Number of parameters": len(arg_names)})
                # Continue to visit the rest of the tree
                self.generic_visit(node)

        finder = RuleFinder()
        finder.visit(tree)

        return finder.endpoints

    def _discover_legacy_rule_language_endpoints_in_file(self, filename):
        endpoints = []
        with open(filename, "r") as file:
            for line in file:
                m = re.match("^(\w+)\s*\((.+)\)\s*\{\s*$", line)
                if m:
                    function_name = m.group(1)
                    args = m.group(2).replace(" ", "").split(",")
                    if not re.match("^(py_)?ac[A-Z]", function_name):
                        endpoints.append({"Endpoint name": function_name,
                                          "Endpoint type": "regular_legacy",
                                          "Number of parameters": len(args)})
        return endpoints
