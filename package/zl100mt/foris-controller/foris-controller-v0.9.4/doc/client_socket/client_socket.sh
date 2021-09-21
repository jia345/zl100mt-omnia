#!/bin/sh

# read socket path from env
SOCKET_PATH=${SOCKET_PATH-/var/run/foris-controller-client.sock}

socket_input() {
	local length=$(echo -n "$1"| wc -c)
	local l1=$(( $length / (256 * 256 * 256) ))
	local l2=$(( ($length / (256 * 256)) % 256 ))
	local l3=$(( ($length / 256) % 256 ))
	local l4=$(( $length % 256 ))
	printf "$(printf "\\%03o\\%03o\\%03o\\%03o" "$l4" "$l3" "$l2" "$l1")"
	echo -n "$1"
}

# send message end write output (if present) (length bytes from output)
socket_input "$1" | socat - UNIX-CLIENT:"$SOCKET_PATH" | cut -c 5-
