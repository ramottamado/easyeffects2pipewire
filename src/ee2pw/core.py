from pathlib import Path
from typing import Any

from .links import create_inputs, create_links, create_outputs
from .plugins import PARSERS, SUPPORTED_PLUGINS, parse_convolver
from .plugins._convert import parse_bool
from .util import load_config

AUDIO_CHANNELS = 2
AUDIO_POSITION = ["FL", "FR"]

DEFAULT_IRS_DIR: Path = Path("/etc/pipewire/pipewire.conf.d")


def builder(
    filepath: str,
    filter_chain_name: str,
    irs_dir: str | None = None,
    smart_filter_target: str | None = None,
) -> dict:
    config: dict[Any, Any] = load_config(filepath)
    ee_output: dict[Any, Any] = config.get("output", {})
    plugins: dict[str, str] = {
        str(plugin): str(plugin).replace("#", "_")
        for plugin in ee_output.get("plugins_order", [])
        if str(plugin).split("#")[0] in SUPPORTED_PLUGINS
        # the builtin convolver has no enable control, so drop it when bypassed
        and not (
            str(plugin).startswith("convolver")
            and parse_bool(ee_output.get(plugin, {}), "bypass", True)
        )
    }

    if not plugins:
        # only bypassed convolvers were left: emit a pass-through chain
        if any(
            str(plugin).startswith("convolver")
            for plugin in ee_output.get("plugins_order", [])
        ):
            return create_module(
                filter_chain_name, create_passthrough_graph(), smart_filter_target
            )

        raise ValueError(f"no supported, active output plugins in {filepath}")

    nodes: list[dict[str, str | dict[str, float]]] = [
        parse_node(ee_output.get(ee_plugin, {}), pw_node_name)
        for ee_plugin, pw_node_name in plugins.items()
        if not ee_plugin.startswith("convolver")
    ]

    convolver_nodes: list[dict[str, str | dict[str, float | str]]] = [
        item
        for ee_plugin, pw_node_name in plugins.items()
        for item in parse_convolver(
            ee_output.get(ee_plugin, {}),
            pw_node_name,
            Path(irs_dir) if irs_dir else DEFAULT_IRS_DIR,
        )
        if ee_plugin.startswith("convolver")
    ]

    links: list[dict[str, str]] = create_links(list(plugins.values()))
    inputs: list[str] = create_inputs(list(plugins.values()))
    outputs: list[str] = create_outputs(list(plugins.values()))

    filter_graph: dict[str, list] = {
        "nodes": nodes + convolver_nodes,
        "links": links,
        "inputs": inputs,
        "outputs": outputs,
    }

    return create_module(filter_chain_name, filter_graph, smart_filter_target)


def create_passthrough_graph() -> dict[str, list]:
    nodes: list[dict[str, str]] = [
        {"type": "builtin", "name": f"copy_{side}", "label": "copy"}
        for side in ("l", "r")
    ]

    return {
        "nodes": nodes,
        "links": [],
        "inputs": ["copy_l:In", "copy_r:In"],
        "outputs": ["copy_l:Out", "copy_r:Out"],
    }


def create_module(
    filter_chain_name: str,
    filter_graph: dict[str, list],
    smart_filter_target: str | None = None,
) -> dict:
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
    for prefix, parser in PARSERS.items():
        if ee_id.startswith(prefix):
            return parser(config, ee_id)

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
        "target.object": smart_filter_target,
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
