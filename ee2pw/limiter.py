from typing import Any
from .util import db_to_linear

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://lsp-plug.in/plugins/lv2/sc_limiter_stereo"

LIMITER_MODE_MAP: dict[str, float] = {
    "Herm Thin": 0.0,
    "Herm Wide": 1.0,
    "Herm Tail": 2.0,
    "Herm Duck": 3.0,
    "Exp Thin": 4.0,
    "Exp Wide": 5.0,
    "Exp Tail": 6.0,
    "Exp Duck": 7.0,
    "Line Thin": 8.0,
    "Line Wide": 9.0,
    "Line Tail": 10.0,
    "Line Duck": 11.0,
}

LIMITER_OVS_MAP: dict[str, float] = {
    "Half x8/16 bit": 9.0,
    "None": 0.0,
    "Half x2/16 bit": 1.0,
    "Half x8/24 bit": 10.0,
    "Half x6/24 bit": 8.0,
    "Half x6/16 bit": 7.0,
    "Full x2/16 bit": 11.0,
    "Half x3/24 bit": 4.0,
    "Half x4/16 bit": 5.0,
    "Half x3/16 bit": 3.0,
    "Half x2/24 bit": 2.0,
    "Half x4/24 bit": 6.0,
    "Full x2/24 bit": 12.0,
    "Full x3/16 bit": 13.0,
    "Full x3/24 bit": 14.0,
    "Full x4/16 bit": 15.0,
    "Full x4/24 bit": 16.0,
    "Full x6/16 bit": 17.0,
    "Full x6/24 bit": 18.0,
    "Full x8/16 bit": 19.0,
    "Full x8/24 bit": 20.0,
    "True Peak/16 bit": 21.0,
    "True Peak/24 bit": 22.0,
}


def parse_limiter(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse limiter settings.

    :param data: EasyEffects limiter configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed limiter settings
    :rtype: dict
    """
    return {
        "type": PLUGIN_TYPE,
        "name": pw_node_name,
        "plugin": PLUGIN_URI,
        "control": {
            "enabled": 0.0 if bool(ee_config.get("bypass", False)) else 1.0,
            "alr": 1.0 if bool(ee_config.get("alr", False)) else 0.0,
            "alr_at": ee_config.get("alr-attack", 5.0),
            "knee": db_to_linear(ee_config.get("alr-knee", 0.0)),
            "alr_rt": ee_config.get("alr-release", 50.0),
            "at": ee_config.get("attack", 0.0),
            "g_in": db_to_linear(ee_config.get("input-gain", 0.0)),
            "lk": ee_config.get("lookahead", 5.0),
            "mode": LIMITER_MODE_MAP.get(ee_config.get("mode", "Herm Thin"), 0.0),
            "g_out": db_to_linear(ee_config.get("output-gain", 0.0)),
            "ovs": LIMITER_OVS_MAP.get(ee_config.get("oversampling", "None"), 0.0),
            "rt": ee_config.get("release", 5.0),
            "slink": ee_config.get("stereo-link", 100.0),
            "th": db_to_linear(ee_config.get("threshold", 0.0)),
        },
    }
