#!/bin/env bash

set -eo pipefail

DEBUG=0

if [[ $DEBUG -eq 1 ]]; then
	set -x
fi

SCRIPT_DIR="$( cd -P "$( dirname "$0" )" && pwd )"
. "$SCRIPT_DIR/utils.sh"

help() {
	echo "Usage: $0 <node_name> <subcommand>"
	echo ""
	echo "Available subcommands:"
	echo "  help                   Show this help message"
	echo "  enable                 Enable the smart filter"
	echo "  disable                Disable the smart filter"
	echo "  status                 Show whether the smart filter is enabled"
	echo ""
	echo "Example:"
	echo "  $0 <node_name> enable"
}

enable_smart_filter() {
	local node_id=$1
	log "INFO" "Enabling smart filter on node $node_id"

	set_filter_metadata "$node_id" "filter.smart.disabled" "false"
}

disable_smart_filter() {
	local node_id=$1
	log "INFO" "Disabling smart filter on node $node_id"

	set_filter_metadata "$node_id" "filter.smart.disabled" "true"
}

smart_filter_status() {
	local node_id=$1
	local disabled source

	# Same precedence as WirePlumber's filter-utils.lua: metadata, then node property, then not disabled.
	disabled=$(get_filter_metadata "$node_id" "filter.smart.disabled")
	source="filters metadata"
	if [ -z "$disabled" ]; then
		disabled=$(get_node_prop "$node_id" "filter.smart.disabled")
		source="node property"
	fi
	if [ -z "$disabled" ]; then
		disabled="false"
		source="default"
	fi

	if [ "$disabled" == "true" ]; then
		log "INFO" "Smart filter on node $node_id is disabled ($source)"
	else
		log "INFO" "Smart filter on node $node_id is enabled ($source)"
	fi
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

	if [ "$subcommand" == "help" ]; then
		help
		exit 0
	fi

	node_id=$(get_pw_node_id_by_name "$node_name")
	if [ -z "$node_id" ]; then
		log "ERROR" "Node with name '$node_name' not found."
		exit 1
	fi

	if [ "$(get_node_prop "$node_id" "filter.smart")" != "true" ]; then
		log "ERROR" "Node '$node_name' is not a smart filter (filter.smart is not set)."
		exit 1
	fi

	case $subcommand in
	enable)
		enable_smart_filter "$node_id"
		;;
	disable)
		disable_smart_filter "$node_id"
		;;
	status)
		smart_filter_status "$node_id"
		;;
	*)
		log "ERROR" "Unknown subcommand: $subcommand"
		log "ERROR" "Usage: $0 <node_name> <subcommand>"
		log "ERROR" "Available subcommands: help, enable, disable, status"
		exit 1
		;;
	esac
}

main "$@"
exit 0
