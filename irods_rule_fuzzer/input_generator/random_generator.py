"""Generates random input parameter values for testing
"""
from collections import OrderedDict
import random
import string


class RandomInputGenerator:

    def generate_input(self, endpoint):
        values = []
        for n in range(0, endpoint["Number of input parameters"]):
            values.append(("param" + str(n), self._get_random_string(4, 16),))
        return OrderedDict(values)

    def _get_random_string(self, min_length, max_length):
        length = random.randint(min_length, max_length)
        # We use a custom punctuation array, because of the need to escape
        # some characters when used in rules
        punctuation = ["!", "(", ")", "[", "]", "~", "?", "\\*", "#", "\\$", "\\\"", "=", "<", ">", "_", "-", "|", "^", "&", "@", ":", ";", ".", "%"]
        chars = list(string.ascii_letters + string.digits) + punctuation
        return (''.join(random.choice(chars) for _ in range(length)))
