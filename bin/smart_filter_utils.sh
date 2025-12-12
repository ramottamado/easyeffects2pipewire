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
	echo "  enable                 Enable the smart filter"
	echo "  disable                Disable the smart filter"
	echo ""
	echo "Example:"
	echo "  $0 <node_id> enable"
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

	node_id=$(pw-dump | jq -r '.[] | select(.info.props."node.name"=="'"$node_name"'") | .id')
	if [ -z "$node_id" ]; then
		log "ERROR" "Node with name '$node_name' not found."
		exit 1
	fi

	case $subcommand in
	help)
		help
		;;
	enable)
		enable_smart_filter "$node_id"
		;;
	disable)
		disable_smart_filter "$node_id"
		;;
	*)
		log "ERROR" "Unknown subcommand: $subcommand"
		log "ERROR" "Usage: $0 <subcommand> [options]"
		log "ERROR" "Available subcommands: help, enable, disable"
		exit 1
		;;
	esac
}

main "$@"
exit 0