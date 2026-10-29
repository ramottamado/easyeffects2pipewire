# ee2pw

Convert an EasyEffects preset into a PipeWire filter chain, optionally as a smart filter bound to a
sink.

## Rationale

Since v8.0.0, EasyEffects is built with Qt dependencies. I use GNOME and avoid Qt apps since they
integrate poorly with GNOME ecosystem. It made sense for me to migrate my EasyEffects presets into
PipeWire smart filters.

## Requirements

- Python 3.12+ (no third-party dependencies)
- PipeWire with `libpipewire-module-filter-chain` (smart filters need a recent PipeWire/WirePlumber)
- The LV2 plugins used by your preset: [LSP Plugins](https://lsp-plug.in/) and/or
  [Calf](https://calf-studio-gear.org/) (see [Supported plugins](#supported-plugins))

## Installation

```sh
uv tool install .      # or: pipx install .
```

Or run it from a clone without installing: `uv run ee2pw ...`.

## Usage

```text
usage: ee2pw [-h] -n FILTER_CHAIN_NAME [-t SMART_FILTER_TARGET] [-i IRS_DIR]
             -o OUTPUT
             filename

positional arguments:
  filename              Path to the EasyEffects configuration file.

options:
  -h, --help            show this help message and exit
  -n FILTER_CHAIN_NAME, --filter-chain-name FILTER_CHAIN_NAME
                        Filter chain name.
  -t SMART_FILTER_TARGET, --smart-filter-target SMART_FILTER_TARGET
                        Smart filter target (if any).
  -i IRS_DIR, --irs-dir IRS_DIR
                        IRS directory (if any).
  -o OUTPUT, --output OUTPUT
                        File output.
```

- `-n` sets the chain's description and its node names, lowercased with spaces replaced by `_`:
  `"ThinkPad X13"` gives `input.thinkpad_x13` (the sink apps play to) and `output.thinkpad_x13`.
- `-t` is the `node.name` of the sink to attach to. With it, the chain becomes a smart filter
  (`filter.smart = true`) that WirePlumber inserts in front of that sink. Without it, you get a
  plain filter-chain sink.
- `-i` is the directory holding the convolver's `.irs` impulse files. The default is
  `/etc/pipewire/pipewire.conf.d`.
- The output is JSON, which PipeWire accepts in its config files.

## Example

```sh
ee2pw "Think.json" \
    -n "ThinkPad X13" \
    -t "alsa_output.pci-0000_73_00.6.HiFi__Speaker__sink" \
    -o "thinkpad-x13.conf"
```

Find the sink's node name with `pw-dump` or `wpctl inspect <id>` (`node.name`).

Example presets are in [tests/fixtures/presets/](tests/fixtures/presets/) and their generated
outputs in [tests/fixtures/expected/](tests/fixtures/expected/).

The output contains one `libpipewire-module-filter-chain` with the preset's plugins chained in
EasyEffects order (`filter_0 → bass_enhancer_0 → … → limiter_0`) and these node properties:

```json
"capture.props": {
  "node.name": "input.thinkpad_x13",
  "media.class": "Audio/Sink",
  "filter.smart": true,
  "filter.smart.name": "ThinkPad X13",
  "filter.smart.target": { "node.name": "alsa_output.pci-0000_73_00.6.HiFi__Speaker__sink" }
},
"playback.props": {
  "target.object": "alsa_output.pci-0000_73_00.6.HiFi__Speaker__sink",
  "node.name": "output.thinkpad_x13",
  "node.passive": true,
  "node.dont-fallback": true,
  "node.linger": true
}
```

Install it and restart PipeWire:

```sh
cp thinkpad-x13.conf ~/.config/pipewire/pipewire.conf.d/
systemctl --user restart pipewire wireplumber
```

## Supported plugins

| EasyEffects plugin    | Preset id prefix       | Implementation                         |
| --------------------- | ---------------------- | -------------------------------------- |
| Bass Enhancer         | `bass_enhancer`        | Calf `BassEnhancer`                    |
| Filter                | `filter`               | LSP `filter_stereo`                    |
| Limiter               | `limiter`              | LSP `sc_limiter_stereo`                |
| Multiband Compressor  | `multiband_compressor` | LSP `sc_mb_compressor_stereo`          |
| Stereo Tools          | `stereo_tools`         | Calf `StereoTools`                     |
| Parametric Equalizer  | `equalizer`            | LSP `para_equalizer_x16_lr`            |
| Convolver             | `convolver`            | PipeWire builtin `convolver` (per channel) |

Other plugins in a preset are skipped.

## Caveats

- Only EasyEffects v8.0.0+ presets are supported.
- Only the `output` section of a preset is converted; input presets are ignored.
- Sidechaining is not implemented.
- A bypassed plugin keeps its node but is disabled, except the convolver, which has no enable
  control and is dropped instead.
- The convolver is mono, so it is emitted as two nodes, `<name>_l` and `<name>_r`.
- If the only plugins left are bypassed convolvers, the output is a pass-through chain.
- If a preset contains no supported plugins, `ee2pw` exits with status 1.

## Runtime helper scripts

`scripts/` has Bash helpers for changing a loaded filter chain without restarting PipeWire. They need
`jq`, `pw-cli`, `pw-dump` and `python`, and take the chain's `input.*` node name followed by a
subcommand (`help` lists them):

```sh
scripts/smart_filter_utils.sh input.thinkpad_x13 disable      # also: enable, status
scripts/mb_compressor_utils.sh input.thinkpad_x13 set-gains -f scripts/gains/flat.json
```

`mb_compressor_utils.sh` targets the `multiband_compressor_0` node that `ee2pw` generates; set
`MB_COMPRESSOR` to use another. See [docs/scripts-changes.md](docs/scripts-changes.md) for details.

## Development

```sh
uv sync --locked --all-groups
uv run python -m unittest discover -v -s tests -p 'test_*.py'
uv run ruff check src tests && uv run ruff format src tests

# after an intended output change, regenerate the golden files and review the diff
UPDATE_FIXTURES=1 uv run python -m unittest tests.test_fixtures
```

A devcontainer is included in `.devcontainer/`.

CI runs lint and tests on every push and pull request. To release, bump the version in
`pyproject.toml` and `src/ee2pw/__init__.py`, run `uv lock`, commit, then push an annotated
`vX.Y.Z` tag. The release workflow checks that the tag matches the version, builds the wheel and
sdist, and publishes a GitHub release that uses the tag message as its notes.

## License

MIT
