from typing import Any
from .util import db_to_linear

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://lsp-plug.in/plugins/lv2/sc_mb_compressor_stereo"

MULTIBAND_COMPRESSOR_MODE_MAP: dict[str, float] = {
    "Classic": 0.0,
    "Modern": 1.0,
    "Linear Phase": 2.0,
}

MULTIBAND_COMPRESSOR_CM_MAP: dict[str, float] = {
    "Downward": 0.0,
    "Upward": 1.0,
    "Boosting": 2.0,
}


def parse_multiband_compressor(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse multiband compressor settings.

    :param data: EasyEffects multiband compressor configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed multiband compressor settings
    :rtype: dict
    """
    pw_node_control_config = {}

    pw_node_control_config.update(
        {
            "mode": MULTIBAND_COMPRESSOR_MODE_MAP.get(
                ee_config.get("mode", "Modern"), 1.0
            ),
            "g_in": db_to_linear(ee_config.get("input-gain", 0.0)),
            "g_out": db_to_linear(ee_config.get("output-gain", 0.0)),
        }
    )

    for i in range(0, 8):
        ee_mb_band_config: dict[Any, Any] = ee_config.get(f"band{i}", {})
        band_enabled: bool = bool(ee_mb_band_config.get("enable-band", False))

        if i != 0:  # band0 always active
            pw_node_control_config.update(
                {
                    f"cbe_{i}": (1.0 if band_enabled else 0.0),
                }
            )

            if not band_enabled:
                continue

            pw_node_control_config.update(
                {
                    f"sf_{i}": ee_mb_band_config.get("split-frequency", 0.0),
                }
            )

        pw_node_control_config.update(
            {
                f"al_{i}": db_to_linear(
                    ee_mb_band_config.get("attack-threshold", -12.0)
                ),
                f"at_{i}": ee_mb_band_config.get("attack-time", 0.0),
                f"cm_{i}": MULTIBAND_COMPRESSOR_CM_MAP.get(
                    ee_mb_band_config.get("compressor-mode", "Downward"), 0.0
                ),
                f"kn_{i}": db_to_linear(ee_mb_band_config.get("knee", -6.0)),
                f"mk_{i}": db_to_linear(ee_mb_band_config.get("makeup", 0.0)),
                f"cr_{i}": db_to_linear(ee_mb_band_config.get("ratio", 1.0)),
                f"rt_{i}": ee_mb_band_config.get("release-time", 100.0),
            }
        )

    return {
        "type": PLUGIN_TYPE,
        "name": pw_node_name,
        "plugin": PLUGIN_URI,
        "control": pw_node_control_config,
    }
