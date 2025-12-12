#!/bin/env bash

set -eo pipefail

DEBUG=0

if [[ $DEBUG -eq 1 ]]; then
	set -x
fi

SCRIPT_DIR="$( cd -P "$( dirname "$0" )" && pwd )"
. "$SCRIPT_DIR/utils.sh"

help() {
	echo "Usage: $0 <node_id> <subcommand> [options]"
	echo ""
	echo "Available subcommands:"
	echo "  help                   Show this help message"
	echo "  set-makeup-gain        Set makeup gain for a specific band in dB"
	echo "  set-input-gain         Set input gain in dB"
	echo ""
	echo "set-makeup-gain options:"
	echo "  -b <band>              Band number (0-3)"
	echo "  -g <gain_value>        Gain value to set (dB)"
	echo ""
	echo "set-input-gain options:"
	echo "  -g <gain_value>        Gain value to set (dB)"
	echo ""
	echo "Example:"
	echo "  $0 <node_id> set-makeup-gain -b 2 -g 3"
}

set_input_gain() {
	shift # past node_id
	while getopts "g:" options; do
		case ${options} in
		g)
			gain_value=$OPTARG
			;;
		*)
			log "ERROR" "Usage: $0 -g <gain_value>"
			exit 1
			;;
		esac
	done

	if [ -z "$gain_value" ]; then
		log "ERROR" "gain_value is required."
		log "ERROR" "Usage: $0 -g <gain_value>"
		exit 1
	fi

	log "INFO" "Setting input gain to $gain_value dB on node $node_id"

	set_props_param "$node_id" "multiband_compressor_0:g_in" "$(db_to_linear "$gain_value")"
}

set_makeup_gain() {
	shift # past node_id
	while getopts "b:g:" options; do
		case ${options} in
		b)
			band=$OPTARG
			;;
		g)
			gain_value=$OPTARG
			;;
		*)
			log "ERROR" "Usage: $0 -b <band> -g <gain_value>"
			exit 1
			;;
		esac
	done

	if [ -z "$band" ] || [ -z "$gain_value" ]; then
		log "ERROR" "Both band and gain_value are required."
		log "ERROR" "Usage: $0 -b <band> -g <gain_value>"
		exit 1
	fi

	log "INFO" "Setting makeup gain for band $band to $gain_value dB on node $node_id"

	set_props_param "$node_id" "multiband_compressor_0:mk_$band" "$(db_to_linear "$gain_value")"
}

main() {
	node_name="$1"
	if [ "${node_name}x" == "x" ]; then
		help
		exit 1
	else
		shift # past node_name
	fi

	subcommand="$1"
	if [ "${subcommand}x" == "x" ]; then
		subcommand="help"
	else
		shift # past sub-command
	fi

	node_id=$(get_pw_node_id_by_name "$node_name")
	if [ -z "$node_id" ]; then
		log "ERROR" "Node with name '$node_name' not found."
		exit 1
	fi

	case $subcommand in
	help)
		help
		;;
	set-makeup-gain)
		set_makeup_gain "$node_id" "$@"
		;;
	set-input-gain)
		set_input_gain "$node_id" "$@"
		;;
	*)
		log "ERROR" "Unknown subcommand: $subcommand"
		log "ERROR" "Usage: $0 <subcommand> [options]"
		log "ERROR" "Available subcommands: help, set-makeup-gain, set-input-gain"
		exit 1
		;;
	esac
}

main "$@"
exit 0
