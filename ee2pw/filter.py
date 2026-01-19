from typing import Any
from .util import db_to_linear
from .lv2_wrapper import *

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://lsp-plug.in/plugins/lv2/filter_stereo"

FILTER_FT_MAP = {
    "Lo-shelf": 2.0,
    "Hi-shelf": 3.0,
    "Lo-pass": 0.0,
    "Hi-pass": 1.0,
    "Bell": 4.0,
    "Bandpass": 5.0,
    "Notch": 6.0,
    "Resonance": 7.0,
    "Ladder-pass": 8.0,
    "Ladder-rej": 9.0,
    "Allpass": 10.0,
}

FILTER_FM_MAP = {
    "RLC (MT)": 1.0,
    "RLC (BT)": 0.0,
    "LRX (BT)": 4.0,
    "LRX (MT)": 5.0,
    "BWC (MT)": 3.0,
    "BWC (BT)": 2.0,
    "APO (DR)": 6.0,
}

FILTER_MODE_MAP = {
    "IIR": 0.0,
    "FIR": 1.0,
    "FFT": 2.0,
    "SPM": 3.0,
}

FILTER_S_MAP = {
    "x1": 0.0,
    "x2": 1.0,
    "x16": 7.0,
    "x6": 4.0,
    "x4": 3.0,
    "x3": 2.0,
    "x12": 6.0,
    "x8": 5.0,
}


def parse_filter(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse filter settings.

    :param data: EasyEffects filter configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed filter settings
    :rtype: dict[str, float]
    """
    return {
        "type": PLUGIN_TYPE,
        "name": pw_node_name,
        "plugin": PLUGIN_URI,
        "control": {
            "enabled": parse_bool(ee_config, "bypass", False, True),
            "g_in": parse_float_db(ee_config, "input-gain", 0.0),
            "g_out": parse_float_db(ee_config, "output-gain", 0.0),
            "f": parse_float(ee_config, "frequency", 0.0),
            "w": parse_float(ee_config, "width", 4.0),
            "g": parse_float_db(ee_config, "gain", 0.0),
            "q": parse_float(ee_config, "quality", 0.0),
            "bal": parse_float(ee_config, "balance", 0.0),
            "ft": parse_enum(ee_config, "type", "Lo-pass", FILTER_FT_MAP, 0.0),
            "fm": parse_enum(ee_config, "mode", "RLC (BT)", FILTER_FM_MAP, 0.0),
            "mode": parse_enum(ee_config, "equal-mode", "IIR", FILTER_MODE_MAP, 0.0),
            "s": parse_enum(ee_config, "slope", "x1", FILTER_S_MAP, 0.0),
        },
    }
