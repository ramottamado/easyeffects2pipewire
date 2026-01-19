from ee2pw.lv2_wrapper import *

import unittest


class TestLv2Wrapper(unittest.TestCase):
    def test_parse_bool(self):
        config = {"test_non_inverted": True, "test_inverted": True}

        expected_non_inverted = 1.0
        expected_inverted = 0.0

        expected_default_not_inverted = 1.0
        expected_default_inverted = 0.0

        self.assertEqual(
            expected_non_inverted, parse_bool(config, "test_non_inverted", True, False)
        )

        self.assertEqual(
            expected_inverted, parse_bool(config, "test_inverted", True, True)
        )

        self.assertEqual(
            expected_default_not_inverted,
            parse_bool(config, "nonexistent_key", True, False),
        )

        self.assertEqual(
            expected_default_inverted, parse_bool(config, "nonexistent_key", True, True)
        )
