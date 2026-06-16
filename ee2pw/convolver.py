from pathlib import Path
from typing import Any
from .lv2_wrapper import parse_bool, parse_float, parse_float_db

PLUGIN_TYPE = "builtin"


def parse_convolver(
    ee_config: dict[Any, Any],
    pw_node_name: str,
    irs_dir: Path,
) -> tuple[
    dict[str, str | dict[str, float | str]] | None,
    dict[str, str | dict[str, float | str]] | None,
]:
    """
    Parse convolver settings.

    :param data: EasyEffects convolver configuration data
    :param pw_node_name: PipeWire node name
    :param irs_dir: IRS file directory
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :type irs_dir: Path
    :return: parsed convolver settings
    :rtype: dict
    """
    if parse_bool(ee_config, "bypass", True):
        return (None, None)

    return (
        {
            "type": PLUGIN_TYPE,
            "name": f"{pw_node_name}_l",
            "label": "convolver",
            "config": {
                "filename": str(
                    irs_dir / (ee_config.get("kernel-name", "convolver") + ".irs")
                ),
                "channel": 0,
                "gain": parse_float_db(ee_config, "output-gain", 0.0),
            },
        },
        {
            "type": PLUGIN_TYPE,
            "name": f"{pw_node_name}_r",
            "label": "convolver",
            "config": {
                "filename": str(
                    irs_dir / (ee_config.get("kernel-name", "convolver") + ".irs")
                ),
                "channel": 1,
                "gain": parse_float_db(ee_config, "output-gain", 0.0),
            },
        },
    )
