from typing import Any

from ..util import db_to_linear, format_6f


def parse_bool(
    config: dict[Any, Any],
    config_string: str,
    config_default: bool,
    invert: bool = False,
) -> float:
    return (
        float(not invert)
        if bool(config.get(config_string, config_default))
        else float(invert)
    )


def parse_enum(
    config: dict[Any, Any],
    config_string: str,
    config_default: str,
    enum_map: dict[str, float],
    lv2_default: float,
) -> float:
    return enum_map.get(config.get(config_string, config_default), lv2_default)


def parse_float(
    config: dict[Any, Any], config_string: str, config_default: float
) -> float:
    return format_6f(config.get(config_string, config_default))


def parse_float_db(
    config: dict[Any, Any],
    config_string: str,
    config_default: float,
) -> float:
    config_value: float = float(config.get(config_string, config_default))
    return format_6f(0.0 if config_value < -80.0 else db_to_linear(config_value))
