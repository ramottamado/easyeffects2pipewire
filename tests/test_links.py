from ee2pw.links import create_links, create_inputs, create_outputs
from ee2pw.util import load_config

import unittest, json


class TestLinksParsing(unittest.TestCase):
    def test_parse_links(self):
        # Load a sample configuration for testing
        config = load_config("tests/data/Think.json")

        # Parse the links from the configuration
        parsed_links = create_links(
            [
                str(plugin).replace("#", "_")
                for plugin in config.get("output", {}).get("plugins_order", [])
            ]
        )

        # Expected output (this should be defined based on the sample_config.json)
        expected_links = [
            {"output": "filter_0:out_l", "input": "bass_enhancer_0:in_l"},
            {
                "output": "bass_enhancer_0:out_l",
                "input": "multiband_compressor_0:in_l",
            },
            {
                "output": "multiband_compressor_0:out_l",
                "input": "stereo_tools_0:in_l",
            },
            {"output": "stereo_tools_0:out_l", "input": "limiter_0:in_l"},
            {"output": "filter_0:out_r", "input": "bass_enhancer_0:in_r"},
            {
                "output": "bass_enhancer_0:out_r",
                "input": "multiband_compressor_0:in_r",
            },
            {
                "output": "multiband_compressor_0:out_r",
                "input": "stereo_tools_0:in_r",
            },
            {"output": "stereo_tools_0:out_r", "input": "limiter_0:in_r"},
        ]

        # Assert that the parsed links match the expected output
        self.assertEqual(parsed_links, expected_links)

    def test_parse_inputs(self):
        config = load_config("tests/data/Think.json")

        parsed_inputs = create_inputs(
            [
                str(plugin).replace("#", "_")
                for plugin in config.get("output", {}).get("plugins_order", [])
            ]
        )

        expected_inputs = ["filter_0:in_l", "filter_0:in_r"]

        self.assertEqual(parsed_inputs, expected_inputs)

    def test_parse_outputs(self):
        config = load_config("tests/data/Think.json")

        parsed_outputs = create_outputs(
            [
                str(plugin).replace("#", "_")
                for plugin in config.get("output", {}).get("plugins_order", [])
            ]
        )

        expecter_outputs = ["limiter_0:out_l", "limiter_0:out_r"]

        self.assertEqual(parsed_outputs, expecter_outputs)
