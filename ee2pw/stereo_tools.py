from typing import Any

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://calf.sourceforge.net/plugins/StereoTools"


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
            "stereo_base": ee_config.get("stereo-base", 0.0),
        },
    }
