from typing import Any

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://lsp-plug.in/plugins/lv2/sc_limiter_stereo"

FILTER_MODE_MAP = {
    "IIR": 0.0,
    "FIR": 1.0,
    "FFT": 2.0,
    "SPM": 3.0,
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
            "enabled": 0.0 if bool(ee_config.get("bypass", False)) else 1.0,
            "bal": ee_config.get("balance", 0.0),
            "mode": FILTER_MODE_MAP.get(ee_config.get("equal-mode", "IIR"), 0.0),
            "f": ee_config.get("frequency", 0.0),
            "fm": FILTER_FM_MAP.get(ee_config.get("mode", "RLC (BT)"), 0.0),
            "s": FILTER_S_MAP.get(ee_config.get("slope", "x1"), 0.0),
            "ft": FILTER_FT_MAP.get(ee_config.get("type", "Lo-pass"), 0.0),
            "w": ee_config.get("width", 4.0),
            "q": ee_config.get("quality", 0.0),
        },
    }
