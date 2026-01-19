from typing import Any
from .lv2_wrapper import parse_bool, parse_float, parse_float_db

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://calf.sourceforge.net/plugins/BassEnhancer"


def parse_bass_enhancer(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse bass enhancer settings.

    :param data: EasyEffects bass enhancer configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed bass enhancer settings
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
            "amount": parse_float_db(ee_config, "amount", 0.0),
            "drive": parse_float(ee_config, "harmonics", 8.5),
            "freq": parse_float(ee_config, "scope", 100.0),
            "floor": parse_float(ee_config, "floor", 20.0),
            "blend": parse_float(ee_config, "blend", 0.0),
            "floor_active": parse_bool(ee_config, "floor-active", False),
            "listen": parse_bool(ee_config, "listen", False),
        },
    }
