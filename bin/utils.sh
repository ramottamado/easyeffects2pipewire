#!/bin/bash

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

db_to_linear() {
	local db_value=$1
	python -c "print(10 ** ($db_value / 20))"
}

get_pw_node_id_by_name() {
	local node_name=$1
	pw-dump | jq -r '.[] | select(.info.props."node.name"=="'"$node_name"'") | .id'
}

set_props_param() {
	local node_id=$1
	local param_name=$2
	local param_value=$3

	log "DEBUG" "$(pw-cli set-param "$node_id" Props "{ params = [ \"$param_name\" $param_value ] }" 2>&1)"
}

set_filter_metadata() {
	local node_id=$1
	local key=$2
	local value=$3

	log "DEBUG" "$(pw-metadata -n filters "$node_id" "$key" "$value" "Spa:String:JSON" 2>&1)"
}
