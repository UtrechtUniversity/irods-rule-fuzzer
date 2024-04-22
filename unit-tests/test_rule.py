# -*- coding: utf-8 -*-

"""Unit tests for rule execution code
"""

__copyright__ = 'Copyright (c) 2024, Utrecht University'
__license__   = 'MIT license, see LICENSE'

from collections import OrderedDict
import sys
from unittest import TestCase

sys.path.append("../irods_rule_fuzzer")

from rule import _construct_rule_body, _construct_input_params


class RuleTest(TestCase):
    def test_construct_rule_body(self):
        expected_result = """myRule {
 fuzzCheck (*logmarker,*outparam1);
 writeLine("stdout","*outparam1");}"""
        self.assertEqual(_construct_rule_body(
            OrderedDict([('logmarker', 'Parameter type discovery ended.')]),
            1,
            "fuzzCheck"), expected_result)

    def test_construct_input_params(self):
        self.assertEqual(_construct_input_params(
            OrderedDict([('logmarker', 'Parameter type discovery starting')])),
            {'*logmarker': '"Parameter type discovery starting"'})
