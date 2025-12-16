from typing import Any

from .filter import parse_filter
from .limiter import parse_limiter
from .links import create_inputs, create_links, create_outputs
from .bass_enhancer import parse_bass_enhancer
from .stereo_tools import parse_stereo_tools
from .multiband_compressor import parse_multiband_compressor

from .util import load_config

AUDIO_CHANNELS = 2
AUDIO_POSITION = ["FL", "FR"]


def builder(
    filepath: str,
    filter_chain_name: str,
    smart_filter_target: str | None = None,
) -> dict:
    config: dict[Any, Any] = load_config(filepath)
    ee_output: dict[Any, Any] = config.get("output", {})
    plugins: dict[str, str] = {
        str(plugin): str(plugin).replace("#", "_")
        for plugin in ee_output.get("plugins_order", [])
    }

    nodes: list[dict[str, str | dict[str, float]]] = [
        parse_node(ee_output.get(ee_plugin, {}), pw_node_name)
        for ee_plugin, pw_node_name in plugins.items()
    ]

    links: list[dict[str, str]] = create_links(list(plugins.values()))
    inputs: list[str] = create_inputs(list(plugins.values()))
    outputs: list[str] = create_outputs(list(plugins.values()))

    filter_graph: dict[str, list] = {
        "nodes": nodes,
        "links": links,
        "inputs": inputs,
        "outputs": outputs,
    }

    capture_props: dict[str, Any] = create_capture_props(
        filter_chain_name, smart_filter_target
    )

    playback_props: dict[str, Any] = create_playback_props(
        filter_chain_name, smart_filter_target
    )

    args = {
        "node.description": filter_chain_name,
        "media.name": filter_chain_name,
        "filter.graph": filter_graph,
        "audio.channels": AUDIO_CHANNELS,
        "audio.position": AUDIO_POSITION,
        "capture.props": capture_props,
        "playback.props": playback_props,
    }

    module = {
        "name": "libpipewire-module-filter-chain",
        "args": args,
    }

    return {"context.modules": [module]}


def parse_node(config: dict[str, Any], ee_id: str) -> dict[str, str | dict[str, float]]:
    if ee_id.startswith("bass_enhancer"):
        return parse_bass_enhancer(config, ee_id)
    elif ee_id.startswith("filter"):
        return parse_filter(config, ee_id)
    elif ee_id.startswith("limiter"):
        return parse_limiter(config, ee_id)
    elif ee_id.startswith("multiband_compressor"):
        return parse_multiband_compressor(config, ee_id)
    elif ee_id.startswith("stereo_tools"):
        return parse_stereo_tools(config, ee_id)

    return {}


def create_capture_props(
    filter_chain_name: str, smart_filter_target: str | None = None
) -> dict[str, Any]:
    snake_case_filtered_chain_name = filter_chain_name.replace(" ", "_").lower()

    capture_props: dict[str, Any] = {
        "node.name": f"input.{snake_case_filtered_chain_name}",
        "media.class": "Audio/Sink",
    }

    if smart_filter_target:
        capture_props.update(
            {
                "filter.smart": True,
                "filter.smart.name": filter_chain_name,
                "filter.smart.target": {"node.name": smart_filter_target},
            }
        )

    return capture_props


def create_playback_props(
    filter_chain_name: str, smart_filter_target: str | None = None
) -> dict[str, Any]:
    snake_case_filter_chain_name = filter_chain_name.replace(" ", "_").lower()

    playback_props: dict[str, Any] = {
        "node.name": f"output.{snake_case_filter_chain_name}",
        "node.passive": True,
    }

    if smart_filter_target:
        playback_props.update(
            {
                "node.dont-fallback": True,
                "node.linger": True,
            }
        )

    return playback_props
