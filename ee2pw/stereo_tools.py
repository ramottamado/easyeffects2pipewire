from typing import Any
from .util import db_to_linear
from .lv2_wrapper import parse_bool, parse_enum, parse_float, parse_float_db

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://calf.sourceforge.net/plugins/StereoTools"

STEREO_TOOLS_MODE_MAP: dict[str, float] = {
    "LR > LR (Stereo Default)": 0.0,
    "LR > MS (Stereo to Mid-Side)": 1.0,
    "MS > LR (Mid-Side to Stereo)": 2.0,
    "LR > LL (Mono Left Channel)": 3.0,
    "LR > RR (Mono Right Channel)": 4.0,
    "LR > L+R (Mono Sum L+R)": 5.0,
    "LR > RL (Stereo Flip Channels)": 6.0,
}


def parse_stereo_tools(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse stereo tools settings.

    :param data: EasyEffects stereo tools configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed stereo tools settings
    :rtype: dict
    """
    return {
        "type": PLUGIN_TYPE,
        "name": pw_node_name,
        "plugin": PLUGIN_URI,
        "control": {
            "bypass": parse_bool(ee_config, "bypass", False),
            "level_in": parse_float_db(ee_config, "input-gain", 0.0),
            "level_out": parse_float_db(ee_config, "output-gain", 0.0),
            "balance_in": parse_float(ee_config, "balance-in", 0.0),
            "balance_out": parse_float(ee_config, "balance-out", 0.0),
            "softclip": parse_bool(ee_config, "softclip", False),
            "mutel": parse_bool(ee_config, "mutel", False),
            "muter": parse_bool(ee_config, "muter", False),
            "phasel": parse_bool(ee_config, "phasel", False),
            "phaser": parse_bool(ee_config, "phaser", False),
            "mode": parse_enum(
                ee_config,
                "mode",
                "LR > LR (Stereo Default)",
                STEREO_TOOLS_MODE_MAP,
                0.0,
            ),
            "slev": parse_float_db(ee_config, "slev", 0.0),
            "sbal": parse_float(ee_config, "sbal", 0.0),
            "mlev": parse_float_db(ee_config, "mlev", 0.0),
            "mpan": parse_float(ee_config, "mpan", 0.0),
            "stereo_base": parse_float(ee_config, "stereo-base", 0.0),
            "delay": parse_float(ee_config, "delay", 0.0),
            "sc_level": parse_float_db(ee_config, "sc-level", 0.0),
            "stereo_phase": parse_float(ee_config, "stereo-phase", 0.0),
        },
    }
