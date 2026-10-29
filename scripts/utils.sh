#!/bin/bash

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
		echo -e "\e[31m[ERROR] $message\e[0m" >&2
		;;
	DEBUG)
		if [[ -n $DEBUG && $DEBUG -eq 1 ]]; then
			echo -e "\e[34m[DEBUG] $message\e[0m"
		fi
		;;
	*)
		echo "$message"
		;;
	esac
}

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

db_to_linear() {
	local db_value=$1
	python -c "import sys; print(10 ** (float(sys.argv[1]) / 20))" "$db_value"
}

is_number() {
	[[ $1 =~ ^-?[0-9]+([.][0-9]+)?$ ]]
}

get_pw_node_id_by_name() {
	local node_name=$1
	pw-dump | jq -r --arg name "$node_name" '.[] | select(.info.props."node.name"==$name) | .id'
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

get_filter_metadata() {
	local node_id=$1
	local key=$2

	pw-dump | jq -r --argjson id "$node_id" --arg key "$key" '
		.[]
		| select(.type == "PipeWire:Interface:Metadata" and .props."metadata.name" == "filters")
		| .metadata[]?
		| select(.subject == $id and .key == $key)
		| .value | tostring'
}

get_node_prop() {
	local node_id=$1
	local key=$2

	pw-dump | jq -r --argjson id "$node_id" --arg key "$key" '.[] | select(.id == $id) | .info.props[$key] // empty | tostring'
}
