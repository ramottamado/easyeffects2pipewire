# Changes to `scripts/`

Changes to the runtime helper scripts (`mb_compressor_utils.sh`, `smart_filter_utils.sh`, `utils.sh`) made after they moved from `bin/` to `scripts/`.

All scripts take a PipeWire node name first, then a subcommand. The node name is the filter chain's capture node, e.g. `input.internal_speaker`, not the `output.*` node.

## Bug fixes

### `mb_compressor_utils.sh`

- `set-input-gain` wrote to `multiband_compressor_1:g_in`. It now writes to `multiband_compressor_0:g_in`, the node name `ee2pw` generates, so `set-gains` now sets the input gain as well.
- `disable` set `multiband_compressor_0:enabled` to `1`, which enabled the compressor. It now sets `0`.
- `set-gains` passed a missing key to `db_to_linear` as `null`, which crashed Python. Missing keys are now skipped.
- Band numbers, gains, frequencies and on/off values are checked before anything is sent. Invalid input exits with status 1.
- Option variables (`band`, `gain_value`, …) are now `local`, so values no longer carry over between calls inside `set-gains`.

### `utils.sh`

- `log` was defined after the dependency checks that call it, so a missing `jq`/`pw-cli`/`pw-dump`/`python` printed `log: command not found` instead of the real message. `log` now comes first.
- The DEBUG check was `[[ -z $DEBUG && $DEBUG -eq 1 ]]`, which is never true, so DEBUG output never printed. It is now `-n`.
- `ERROR` messages go to stderr.
- `db_to_linear` passes the value to Python as an argument instead of pasting it into the code.
- `get_pw_node_id_by_name` passes the node name to `jq` with `--arg` instead of building the filter by string concatenation.

### `smart_filter_utils.sh`

- `enable`, `disable` and `status` refuse nodes that are not smart filters. The node must have `filter.smart = true`, otherwise the script exits with status 1. Before this change, the script would write `filter.smart.disabled` to the `filters` metadata for any node, such as an ALSA source, where it had no effect.
- The node lookup now uses `get_pw_node_id_by_name` from `utils.sh` instead of its own copy.

### Help text (both scripts)

- The usage line said `<node_id>`; the scripts take a node name.
- Band ranges said `0-8`; the compressor has 8 bands, `0-7`.
- The "unknown subcommand" error now lists every subcommand.
- `help` works without looking up a node first.

## Features implemented

These were missing pieces the existing code or data already pointed to.

- **Split frequencies.** The gain files in `scripts/gains/` contain `split-frequency` for bands 1–7, but nothing applied it. There is now a `set-split-frequency -b <1-7> -f <Hz>` subcommand (writes `sf_<band>`), and `set-gains` applies `split-frequency` from the gain file along with `makeup`.

## Additions not asked for by the existing code

These were added without anything in the code or data asking for them, and are still to be reviewed. They may be removed.

| Script | Addition | Writes / reads |
|---|---|---|
| `mb_compressor_utils.sh` | `enable` | `enabled` = `1` |
| `mb_compressor_utils.sh` | `set-output-gain -g <dB>` | `g_out` |
| `mb_compressor_utils.sh` | `output-gain` key in `set-gains` files | `g_out` |
| `mb_compressor_utils.sh` | `set-mute -b <0-7> -v <0/1>` | `bm_<band>` |
| `mb_compressor_utils.sh` | `set-band-enabled -b <1-7> -v <0/1>` | `cbe_<band>` |
| `mb_compressor_utils.sh` | `set-band-compressor -b <0-7> -v <0/1>` | `ce_<band>` |
| `mb_compressor_utils.sh` | `MB_COMPRESSOR` environment variable | Compressor node name, default `multiband_compressor_0` |
| `smart_filter_utils.sh` | `status` | Reads `filter.smart.disabled` from the `filters` metadata, then the node property, else reports enabled |
| `utils.sh` | `get_filter_metadata`, `get_node_prop` | Helpers for `status` and the smart-filter check |

`ee2pw` never sets `filter.smart.disabled` as a node property, so the node-property fallback in `status` only matters for hand-written configs.

## How this was verified

The devcontainer has no PipeWire, so the scripts were run with stub `pw-cli` and `pw-metadata` commands that record their arguments, and a `pw-dump` that prints `tests/pipewire/pw-dump.log` (captured from the host running PipeWire 1.6.10 and WirePlumber 0.5.18).

- Every control the compressor script writes (`enabled`, `g_in`, `g_out`, `mk_/bs_/bm_/ce_` for bands 0–7, `sf_/cbe_` for bands 1–7) exists on the captured `input.samsung_usb_c_earphones` node as `multiband_compressor_0:*`.
- `set-gains -f scripts/gains/flat.json` produces 16 `pw-cli set-param` calls (input gain, then split frequency and makeup per band).
- `smart_filter_utils.sh` accepts `input.internal_speaker` and rejects `output.internal_speaker` (no `filter.smart`).

None of the changed scripts has been run against a live PipeWire yet.
