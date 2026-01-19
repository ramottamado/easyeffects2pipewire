from typing import Any
from .lv2_wrapper import parse_bool, parse_enum, parse_float, parse_float_db

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

LIMITER_DITHERING_MAP: dict[str, float] = {
    "None": 0.0,
    "7bit": 1.0,
    "8bit": 2.0,
    "11bit": 3.0,
    "12bit": 4.0,
    "15bit": 5.0,
    "16bit": 6.0,
    "23bit": 7.0,
    "24bit": 8.0,
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
            "mode": parse_enum(ee_config, "mode", "Herm Thin", LIMITER_MODE_MAP, 0.0),
            "ovs": parse_enum(ee_config, "oversampling", "None", LIMITER_OVS_MAP, 0.0),
            "dith": parse_enum(
                ee_config, "dithering", "None", LIMITER_DITHERING_MAP, 0.0
            ),
            "enabled": parse_bool(ee_config, "bypass", False, True),
            "g_in": parse_float_db(ee_config, "input-gain", 0.0),
            "g_out": parse_float_db(ee_config, "output-gain", 0.0),
            "lk": parse_float(ee_config, "lookahead", 5.0),
            "at": parse_float(ee_config, "attack", 0.0),
            "rt": parse_float(ee_config, "release", 5.0),
            "th": parse_float_db(ee_config, "threshold", 0.0),
            "slink": parse_float(ee_config, "stereo-link", 100.0),
            "alr_at": parse_float(ee_config, "alr-attack", 5.0),
            "alr_rt": parse_float(ee_config, "alr-release", 50.0),
            "knee": parse_float_db(ee_config, "alr-knee", 0.0),
            "alr": parse_bool(ee_config, "alr", False),
            "boost": parse_bool(ee_config, "gain-boost", False),
        },
    }
