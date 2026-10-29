from collections.abc import Callable
from typing import Any

from .bass_enhancer import parse_bass_enhancer
from .convolver import parse_convolver
from .filter import parse_filter
from .limiter import parse_limiter
from .multiband_compressor import parse_multiband_compressor
from .parametric_eq import parse_parametric_eq
from .stereo_tools import parse_stereo_tools

# EasyEffects plugin id prefix -> parser. The convolver is not listed here
# because it needs the IRS directory and emits one node per channel.
PARSERS: dict[str, Callable[[dict[Any, Any], str], dict[str, Any]]] = {
    "bass_enhancer": parse_bass_enhancer,
    "filter": parse_filter,
    "limiter": parse_limiter,
    "multiband_compressor": parse_multiband_compressor,
    "stereo_tools": parse_stereo_tools,
    "equalizer": parse_parametric_eq,
}

SUPPORTED_PLUGINS: list[str] = [*PARSERS, "convolver"]

__all__ = ["PARSERS", "SUPPORTED_PLUGINS", "parse_convolver"]
