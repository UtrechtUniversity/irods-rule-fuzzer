"""This class translates generated input for rules
   into the API format for Yoda API rules.
"""

import base64
import json
import zlib


class YodaAPIInputTranslator:
    def __init__(self):
        pass

    def translate_input(self, endpoint, parameters):
        inputs = {}
        parameter_names = endpoint["Input parameter names"]
        for n in range(len(parameter_names)):
            inputs[parameter_names[n]] = list(parameters.items())[n][1]
        json_input = json.dumps(inputs)
        compressed_content = zlib.compress(json_input.encode("utf-8"))

        return {"input": base64.b64encode(compressed_content).decode("utf-8")}
