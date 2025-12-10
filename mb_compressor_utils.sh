#!/bin/env bash

set -eo pipefail

DEBUG=0

if [[ $DEBUG -eq 1 ]]; then
	set -x
fi

log() {
	local level="$1"
	shift
	local message="$*"
	case "$level" in
	INFO)
		echo -e "\e[32m[INFO] $message\e[0m"
		;;
	WARN)
		echo -e "\e[33m[WARN] $message\e[0m"
		;;
	ERROR)
		echo -e "\e[31m[ERROR] $message\e[0m"
		;;
	DEBUG)
		echo -e "\e[34m[DEBUG] $message\e[0m"
		;;
	*)
		echo "$message"
		;;
	esac
}

# shellcheck disable=SC2329
clean_exit() {
	local exit_code=$?
	exit "$exit_code"
}

trap clean_exit EXIT

db_to_linear() {
	local db_value=$1
	python -c "print(10 ** ($db_value / 20))"
}

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

set_param() {
	local node_id=$1
	shift
	local param_name=$1
	shift
	local param_value=$1

	log "DEBUG" "$(pw-cli set-param "$node_id" Props "{ params = [ \"$param_name\" $param_value ] }" 2>&1)"
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

	set_param "$node_id" "multiband_compressor_0:g_in" "$(db_to_linear "$gain_value")"
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

	set_param "$node_id" "multiband_compressor_0:mk_$band" "$(db_to_linear "$gain_value")"
}

main() {
	if ! command -v jq &>/dev/null; then
		log "ERROR" "jq is required but not installed. Please install jq to proceed."
		exit 1
	fi

	if ! command -v pw-cli &>/dev/null; then
		log "ERROR" "pw-cli is required but not installed. Please install PipeWire to proceed."
		exit 1
	fi

	if ! command -v pw-dump &>/dev/null; then
		log "ERROR" "pw-dump is required but not installed. Please install PipeWire to proceed."
		exit 1
	fi

	if ! command -v python &>/dev/null; then
		log "ERROR" "Python is required but not installed. Please install Python to proceed."
		exit 1
	fi

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

	node_id=$(pw-dump | jq -r '.[] | select(.info.props."node.name"=="'"$node_name"'") | .id')
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
