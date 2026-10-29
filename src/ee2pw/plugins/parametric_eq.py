from typing import Any

from ._convert import parse_bool, parse_enum, parse_float, parse_float_db

PLUGIN_TYPE = "lv2"
PLUGIN_URI = "http://lsp-plug.in/plugins/lv2/para_equalizer_x16_lr"

PARAMETRIC_EQ_MODE_MAP: dict[str, float] = {
    "IIR": 0.0,
    "FIR": 1.0,
    "FFT": 2.0,
    "SPM": 3.0,
}

PARAMETRIC_EQ_TYPE_MAP: dict[str, float] = {
    "Off": 0.0,
    "Bell": 1.0,
    "Hi-pass": 2.0,
    "Hi-shelf": 3.0,
    "Lo-pass": 4.0,
    "Lo-shelf": 5.0,
    "Notch": 6.0,
    "Resonance": 7.0,
    "Allpass": 8.0,
    "Bandpass": 9.0,
    "Ladder-pass": 10.0,
    "Ladder-rej": 11.0,
}

PARAMETRIC_EQ_SLOPE_MAP: dict[str, float] = {"x1": 0.0, "x2": 1.0, "x3": 2.0, "x4": 3.0}

PARAMETRIC_EQ_FREQ_MODE_MAP: dict[str, float] = {
    "RLC (BT)": 0.0,
    "RLC (MT)": 1.0,
    "BWC (BT)": 2.0,
    "BWC (MT)": 3.0,
    "LRX (BT)": 4.0,
    "LRX (MT)": 5.0,
    "APO (DR)": 6.0,
}


def parse_parametric_eq(
    ee_config: dict[Any, Any], pw_node_name: str
) -> dict[str, str | dict[str, float]]:
    """
    Parse parametric EQ settings.

    :param data: EasyEffects parametric EQ configuration data
    :param pw_node_name: PipeWire node name
    :type data: dict[Any, Any]
    :type pw_node_name: str
    :return: parsed parametric EQ settings
    :rtype: dict
    """
    pw_node_control_config = {}

    pw_node_control_config.update(
        {
            "enabled": parse_bool(ee_config, "bypass", False, True),
            "g_in": parse_float_db(ee_config, "input-gain", 0.0),
            "g_out": parse_float_db(ee_config, "output-gain", 0.0),
            "mode": parse_enum(ee_config, "mode", "IIR", PARAMETRIC_EQ_MODE_MAP, 0.0),
        },
    )

    num_bands: int = ee_config.get("num-bands", 0)
    left: dict[str, Any] = ee_config.get("left", {})
    right: dict[str, Any] = ee_config.get("right", {})

    for i in range(16):
        if i < num_bands:
            for side, bands in (("l", left), ("r", right)):
                band_config: dict[Any, Any] = bands.get(f"band{i}", {})
                pw_node_control_config.update(
                    {
                        f"ft{side}_{i}": parse_enum(
                            band_config, "type", "Off", PARAMETRIC_EQ_TYPE_MAP, 0.0
                        ),
                        f"fm{side}_{i}": parse_enum(
                            band_config,
                            "mode",
                            "RLC (BT)",
                            PARAMETRIC_EQ_FREQ_MODE_MAP,
                            0.0,
                        ),
                        f"s{side}_{i}": parse_enum(
                            band_config, "slope", "x1", PARAMETRIC_EQ_SLOPE_MAP, 0.0
                        ),
                        f"f{side}_{i}": parse_float(band_config, "frequency", 1000.0),
                        f"g{side}_{i}": parse_float_db(band_config, "gain", 0.0),
                        f"q{side}_{i}": parse_float(band_config, "q", 1.0),
                        f"w{side}_{i}": parse_float(band_config, "width", 4.0),
                        f"xm{side}_{i}": parse_bool(band_config, "mute", False),
                        f"xs{side}_{i}": parse_bool(band_config, "solo", False),
                    }
                )
        else:
            pw_node_control_config.update(
                {
                    f"ftl_{i}": 0.0,
                    f"ftr_{i}": 0.0,
                }
            )

    return {
        "type": PLUGIN_TYPE,
        "name": pw_node_name,
        "plugin": PLUGIN_URI,
        "control": pw_node_control_config,
    }
