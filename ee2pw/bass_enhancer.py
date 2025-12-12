from typing import Any
from .util import db_to_linear

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
            "amount": db_to_linear(ee_config.get("amount", 0.0)),
            "blend": ee_config.get("blend", 0.0),
            "floor": ee_config.get("floor", 20.0),
            "floor_active": (1.0 if ee_config.get("floor-active", False) else 0.0),
            "drive": ee_config.get("harmonics", 8.5),
            "freq": ee_config.get("scope", 100.0),
        },
    }
