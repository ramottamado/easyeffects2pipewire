from typing import Any
from .lv2_wrapper import parse_bool, parse_enum, parse_float, parse_float_db

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://lsp-plug.in/plugins/lv2/sc_mb_compressor_stereo"

MULTIBAND_COMPRESSOR_MODE_MAP: dict[str, float] = {
    "Classic": 0.0,
    "Modern": 1.0,
    "Linear Phase": 2.0,
}

MULTIBAND_COMPRESSOR_ENVELOPE_BOOST_MAP: dict[str, float] = {
    "None": 0.0,
    "Pink BT": 1.0,
    "Pink MT": 2.0,
    "Brown BT": 3.0,
    "Brown MT": 4.0,
}

MULTIBAND_COMPRESSOR_COMPRESSION_MODE_MAP: dict[str, float] = {
    "Downward": 0.0,
    "Upward": 1.0,
    "Boosting": 2.0,
}


def parse_multiband_compressor(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse multiband compressor settings.

    :param data: EasyEffects multiband compressor configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed multiband compressor settings
    :rtype: dict
    """
    pw_node_control_config = {}

    pw_node_control_config.update(
        {
            "enabled": parse_bool(ee_config, "bypass", False, True),
            "g_in": parse_float_db(ee_config, "input-gain", 0.0),
            "g_out": parse_float_db(ee_config, "output-gain", 0.0),
            "g_dry": parse_float_db(ee_config, "dry", 0.0),
            "g_wet": parse_float_db(ee_config, "wet", 0.0),
            "mode": parse_enum(
                ee_config,
                "compressor-mode",
                "Modern",
                MULTIBAND_COMPRESSOR_MODE_MAP,
                1.0,
            ),
            "envb": parse_enum(
                ee_config,
                "envelope-boost",
                "Pink BT",
                MULTIBAND_COMPRESSOR_ENVELOPE_BOOST_MAP,
                1.0,
            ),
            "ssplit": parse_bool(ee_config, "stereo-split", False),
        }
    )

    for i in range(0, 8):
        ee_mb_band_config: dict[Any, Any] = ee_config.get(f"band{i}", {})
        band_enabled: float = parse_bool(ee_mb_band_config, "enable-band", False)

        if i != 0:  # band0 always active
            pw_node_control_config.update(
                {
                    f"cbe_{i}": band_enabled,
                }
            )

            if not bool(band_enabled):
                continue

            pw_node_control_config.update(
                {
                    f"sf_{i}": parse_float(ee_mb_band_config, "split-frequency", 0.0),
                }
            )

        pw_node_control_config.update(
            {
                f"ce_{i}": parse_bool(ee_mb_band_config, "compressor-enable", True),
                f"bs_{i}": parse_bool(ee_mb_band_config, "solo", False),
                f"bm_{i}": parse_bool(ee_mb_band_config, "mute", False),
                f"al_{i}": parse_float_db(ee_mb_band_config, "attack-threshold", -12.0),
                f"at_{i}": parse_float(ee_mb_band_config, "attack-time", 0.0),
                f"rrl_{i}": parse_float_db(ee_mb_band_config, "release-threshold", 0.0),
                f"rt_{i}": parse_float(ee_mb_band_config, "release-time", 100.0),
                f"cr_{i}": parse_float_db(ee_mb_band_config, "ratio", 0.0),
                f"kn_{i}": parse_float_db(ee_mb_band_config, "knee", -6.0),
                f"mk_{i}": parse_float_db(ee_mb_band_config, "makeup", 0.0),
                f"cm_{i}": parse_enum(
                    ee_mb_band_config,
                    "compression-mode",
                    "Downward",
                    MULTIBAND_COMPRESSOR_COMPRESSION_MODE_MAP,
                    0.0,
                ),
                f"bth_{i}": parse_float_db(ee_mb_band_config, "boost-threshold", -72.0),
                f"bsa_{i}": parse_float_db(ee_mb_band_config, "boost-amount", 0.0),
            }
        )

    return {
        "type": PLUGIN_TYPE,
        "name": pw_node_name,
        "plugin": PLUGIN_URI,
        "control": pw_node_control_config,
    }
