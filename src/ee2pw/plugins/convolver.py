from pathlib import Path
from typing import Any

from ._convert import parse_float_db

PLUGIN_TYPE = "builtin"


def parse_convolver(
    ee_config: dict[Any, Any],
    pw_node_name: str,
    irs_dir: Path,
) -> tuple[
    dict[str, str | dict[str, float | str]],
    dict[str, str | dict[str, float | str]],
]:
    """
    Parse convolver settings.

    :param data: EasyEffects convolver configuration data
    :param pw_node_name: PipeWire node name
    :param irs_dir: IRS file directory
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :type irs_dir: Path
    :return: parsed left & right channel convolver nodes
    :rtype: tuple[dict, dict]
    """
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
