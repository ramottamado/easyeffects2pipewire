# ee2pw

Parse EasyEffects JSON config into PipeWire smart filters.

## Rationale

Since v8.0.0, EasyEffects is built with Qt dependencies. I use GNOME and avoids Qt apps since they
integrate poorly with GNOME ecosystem. It made sense for me to migrate my EasyEffects presets into
PipeWire smart filters.

## Caveats

- Only supports EasyEffects v7.2.x
- Only support LV2 plugins
- Only supports filter/preset for output
- Sidechaining is not implemented

## Plugin support

- BassEnhancer (Calf)
- Filter (LSP)
- Limiter (LSP)
- Multi-band Compressor (LSP)
- Stereo tools (Calf)

## Usage

```sh
usage: python -m ee2pw [-h] [-n FILTER_CHAIN_NAME] [-t SMART_FILTER_TARGET] [-o OUTPUT] filename

Parse EasyEffects configuration file.

positional arguments:
  filename              Path to the EasyEffects configuration file.

options:
  -h, --help            show this help message and exit
  -n, --filter-chain-name FILTER_CHAIN_NAME
                        Filter chain name.
  -t, --smart-filter-target SMART_FILTER_TARGET
                        Smart filter target (if any).
  -o, --output OUTPUT   File output.
```

## Example

```bash
python -m ee2pw "extras/presets/Think.json" \
    -n "ThinkPad X13" \
    -t "alsa_output.pci-0000_73_00.6.HiFi__Speaker__sink" \
    -o "extras/examples/think.json"
```