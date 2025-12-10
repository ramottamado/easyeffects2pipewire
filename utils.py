#!/bin/env python3

import json, sys, argparse
from math import log10


def db_to_linear(db: float) -> float:
    """
    Convert decibels to linear scale.

    :param db: decibel value
    :type db: float
    :return: linear scale value
    :rtype: float
    """
    return 10 ** (db / 20)


def linear_to_db(linear: float) -> float:
    """
    Convert linear scale to decibels.

    :param linear: linear scale value
    :type linear: float
    :return: decibel value
    :rtype: float
    """
    if linear <= 0:
        return -float("inf")
    return 20 * log10(linear)


class EasyEffectsParser:
    """
    Parse EasyEffects configuration files into lv2 plugin controls.
    """

    MB_COMPRESSOR_MODE_MAP: dict[str, float] = {
        "CLASSIC": 0.0,
        "MODERN": 1.0,
        "LINEAR PHASE": 2.0,
    }

    MB_COMPRESSOR_CM_MAP: dict[str, float] = {
        "DOWNWARD": 0.0,
        "UPWARD": 1.0,
        "BOOSTING": 2.0,
    }

    def __init__(self, filepath):
        self.data = self.load_config(filepath)

    def load_config(self, filepath: str) -> dict:
        """
        Load configuration file.

        :param self: instance of EasyEffectsParser
        :param filepath: path to configuration file
        :type filepath: str
        :return: parsed configuration data as dictionary
        :rtype: dict[Any, Any]
        """
        with open(filepath, "r") as f:
            data = f.read()
        return json.loads(data)

    def parse_mb_compressor(self, num: int) -> dict:
        """
        Parse multiband compressor settings.

        :param self: instance of EasyEffectsParser
        :param num: plugin number
        :type num: int
        :return: parsed multiband compressor settings
        :rtype: dict[Any, Any]
        """
        parsed_config = {}
        mb_compressor_config: dict = self.data.get("output", {}).get(
            f"multiband_compressor#{num}", {}
        )
        parsed_config.update(
            {
                "mode": self.MB_COMPRESSOR_MODE_MAP.get(
                    str(mb_compressor_config.get("mode", "MODERN")).upper(), 1.0
                ),
                "g_in": db_to_linear(mb_compressor_config.get("input-gain", 0.0)),
                "g_out": db_to_linear(mb_compressor_config.get("output-gain", 0.0)),
            }
        )

        for i in range(1, 8):
            band_config: dict = mb_compressor_config.get(f"band{i}", {})
            parsed_config.update(
                {
                    f"cbe_{i}": (
                        1.0 if bool(band_config.get("enable-band", False)) else 0.0
                    ),
                }
            )
        
        for i in range(1, 8):
            band_config: dict = mb_compressor_config.get(f"band{i}", {})
            parsed_config.update(
                {
                    f"sf_{i}": band_config.get("split-frequency", 0.0),
                }
            )
        
        for i in range(0, 8):
            band_config: dict = mb_compressor_config.get(f"band{i}", {})
            parsed_config.update(
                {
                    f"al_{i}": db_to_linear(band_config.get("attack-threshold", -12.0)),
                    f"at_{i}": band_config.get("attack-time", 0.0),
                    f"cm_{i}": self.MB_COMPRESSOR_CM_MAP.get(
                        str(band_config.get("compressor-mode", "DOWNWARD")).upper(), 0
                    ),
                    f"kn_{i}": db_to_linear(band_config.get("knee", -6.0)),
                    f"mk_{i}": db_to_linear(band_config.get("makeup", 0.0)),
                    f"cr_{i}": db_to_linear(band_config.get("ratio", 1.0)),
                    f"rt_{i}": band_config.get("release-time", 100.0),
                }
            )

        return parsed_config


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Parse EasyEffects configuration file."
    )
    argparser.add_argument(
        "filename", type=str, help="Path to the EasyEffects configuration file."
    )
    argparser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["mb_compressor"],
        help="Type of plugin to parse.",
    )
    args = argparser.parse_args()
    parser = EasyEffectsParser(args.filename)
    if args.mode == "mb_compressor":
        config = parser.parse_mb_compressor(0)
        print(json.dumps(config, indent=4))
