# -*- coding: utf-8 -*-

"""Unit tests for extracting rule data from Yoda ruleset
"""

__copyright__ = 'Copyright (c) 2024, Utrecht University'
__license__   = 'MIT license, see LICENSE'

import sys
from unittest import TestCase

sys.path.append("../irods_rule_fuzzer/endpoint_discovery")

from yoda_ruleset import YodaRulesetEndpointDiscovery

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999


class YodaRulesetDiscoverRulesTest(TestCase):
    def test_discover_yoda_legacy_rules(self):
        expected_result = [{'Endpoint name': 'uuClientZone', 'Endpoint type': 'regular_legacy', 'Number of parameters': 1}, {'Endpoint name': 'uuClientFullNameWrapper', 'Endpoint type': 'regular_legacy', 'Number of parameters': 1}, {'Endpoint name': 'uuGroupCategoryExists', 'Endpoint type': 'regular_legacy', 'Number of parameters': 2}]
        d = YodaRulesetEndpointDiscovery("testdata/yoda-legacy")
        self.assertEqual(d.discover_endpoints(), expected_result)

    def test_discover_yoda_python_rules(self):
        expected_result = [{'Endpoint name': 'rule_group_expiration_date_validate', 'Endpoint type': 'regular_python', 'Number of parameters': 1}]
        d = YodaRulesetEndpointDiscovery("testdata/yoda-python")
        self.assertEqual(d.discover_endpoints(), expected_result)

    def test_discover_yoda_api_rules(self):
        expected_result = [{'Endpoint name': 'api_group_categories', 'Endpoint type': 'yoda_api', 'Number of parameters': 0, 'Parameter names': []}, {'Endpoint name': 'api_group_subcategories', 'Endpoint type': 'yoda_api', 'Number of parameters': 1, 'Parameter names': ['category']}]
        d = YodaRulesetEndpointDiscovery("testdata/yoda-api")
        self.assertEqual(d.discover_endpoints(), expected_result)
