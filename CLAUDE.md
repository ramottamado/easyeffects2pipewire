# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`ee2pw` converts an EasyEffects (v8.0.0+) preset JSON into a PipeWire `libpipewire-module-filter-chain` config (optionally a smart filter bound to a sink). Only the `output` section of presets is handled, only LV2 plugins plus PipeWire's builtin convolver, and sidechaining is not implemented. The package has no runtime dependencies (stdlib only, Python >= 3.12); the dev environment is managed with `uv`.

## Commands

```sh
uv sync --locked --all-groups          # set up venv (devcontainer does this on create)

# Convert a preset (`uv run ee2pw` and `python -m ee2pw` are equivalent)
uv run ee2pw "presets/Think.json" \
    -n "ThinkPad X13" \
    -t "alsa_output.pci-0000_73_00.6.HiFi__Speaker__sink" \
    -o "examples/think.json"
# -n and -o are required (-n derives node names); -t enables smart-filter props;
# -i sets the directory for convolver .irs files (default /etc/pipewire/pipewire.conf.d)

# Tests (unittest, not pytest; run from repo root because test_links loads fixtures by relative path)
uv run python -m unittest discover -v -s tests -p 'test_*.py'
uv run python -m unittest tests.test_links.TestLinksParsing.test_parse_links   # single test

# Regenerate golden outputs after an intended output change (review the diff!)
UPDATE_FIXTURES=1 uv run python -m unittest tests.test_fixtures

uv run ruff check src tests && uv run ruff format src tests
```

The package lives in `src/ee2pw/` (src layout), so it is only importable through the installed editable package — use `uv run`, not a bare `python` outside the venv.

`tests/test_fixtures.py` runs every `tests/fixtures/presets/*.json` through `builder()` and compares it with `tests/fixtures/expected/<same name>.json`. These are copies, deliberately separate from the top-level `presets/`, which change often and, like `examples/`, are gitignored (local working files only).

## Architecture

- `src/ee2pw/core.py` `builder()` is the whole pipeline: load preset → take `output.plugins_order`, keep only entries whose prefix is in `SUPPORTED_PLUGINS` → map EasyEffects ids (`filter#0`) to PipeWire node names (`filter_0`) → dispatch each to its parser via `parse_node()` → build links/inputs/outputs → wrap in `context.modules` with capture/playback props.
- `src/ee2pw/plugins/` has one module per plugin. Each defines `PLUGIN_TYPE`, `PLUGIN_URI` (LSP/Calf LV2 URI), enum maps from EasyEffects string values to LV2 port float values, and a `parse_<plugin>(ee_config, pw_node_name)` returning `{type, name, plugin, control}` keyed by LV2 port symbols. `plugins/__init__.py` holds the `PARSERS` registry (EasyEffects id prefix → parser; note the parametric EQ's prefix is `equalizer`) and derives `SUPPORTED_PLUGINS` from it.
- `plugins/_convert.py` holds the shared value converters used by every parser: `parse_bool` (with `invert`, used for `bypass` → `enabled`), `parse_enum`, `parse_float`, `parse_float_db` (dB → linear, anything below -80 dB becomes 0.0). Values are rounded to 6 decimals via `util.format_6f`.
- Convolver is special and not in `PARSERS`: it is a builtin (not LV2), mono, needs the IRS dir, and is emitted as two nodes `<name>_l` / `<name>_r` (channel 0/1) with `In`/`Out` ports; `builder()` calls `parse_convolver` directly and drops it when bypassed; if only bypassed convolvers remain it emits a pass-through graph of builtin `copy` nodes, and an otherwise empty chain raises `ValueError` (CLI exits 1). `links.py` encodes this port-naming difference (`convolver*_l:In` vs `<lv2>:in_l`) when chaining nodes and choosing the graph's inputs/outputs.
- Adding a plugin: new module in `plugins/`, one entry in `PARSERS`. Touch `links.py` only if its ports aren't `in_l/in_r/out_l/out_r`. New subpackages must be added to `[tool.setuptools] packages` in `pyproject.toml`.
- Output is written as JSON (PipeWire accepts JSON in its conf files). Locally (untracked), `presets/` are source EasyEffects presets, `examples/` are generated outputs, `examples/reference/` are hand-written `.conf` equivalents.

## Shell helpers (`scripts/`)

Runtime tweaking of a loaded filter chain via `pw-cli set-param` / `pw-metadata`; require `jq`, `pw-cli`, `pw-dump`, `python`. All take a PipeWire node name first, then a subcommand (`help` lists them). `utils.sh` is sourced for logging, dB→linear, and node lookup. `mb_compressor_utils.sh` hardcodes control names like `multiband_compressor_0:mk_<band>`, so it depends on the node names `ee2pw` generates; `scripts/gains/` holds the JSON gain files for its `set-gains -f`.
