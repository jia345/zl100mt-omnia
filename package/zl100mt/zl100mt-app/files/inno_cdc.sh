#!/bin/sh

[ -n "$INCLUDE_ONLY" ] || {
	. /lib/functions.sh
	. ../netifd-proto.sh
	init_proto "$@"
}

proto_inno_cdc_init_config() {
	no_device=1
	available=1
	proto_config_add_string "device:device"
	proto_config_add_string delay
	proto_config_add_string mode
}

proto_inno_cdc_setup() {
	local interface="$1"

	local manufacturer initialize connect ifname devname devpath

	local device delay
	json_get_vars device delay

	[ -n "$device" ] || {
		echo "No control device specified"
		proto_notify_error "$interface" NO_DEVICE
		proto_set_available "$interface" 0
		return 1
	}
	[ -e "$device" ] || {
		echo "Control device not valid"
		proto_set_available "$interface" 0
		return 1
	}

	devname="$(basename "$device")"
    logger -t "LTE_Z" $devname
	case "$devname" in
	'tty'*)
		devpath="$(readlink -f /sys/class/tty/$devname/device)"
		ifname="$( ls "$devpath"/../../*/net )"
		;;
	*)
		devpath="$(readlink -f /sys/class/usbmisc/$devname/device/)"
		ifname="$( ls "$devpath"/net )"
		;;
	esac
	[ -n "$ifname" ] || {
		echo "The interface could not be found."
		proto_notify_error "$interface" NO_IFACE
		proto_set_available "$interface" 0
		return 1
	}

	[ -n "$delay" ] && sleep "$delay"

	manufacturer='innofidei'

	json_load "$(cat /etc/gcom/inno_cdc.json)"
	json_select "$manufacturer"
	[ $? -ne 0 ] && {
		echo "Unsupported modem"
		proto_notify_error "$interface" UNSUPPORTED_MODEM
		proto_set_available "$interface" 0
		return 1
	}
	json_get_values initialize initialize
	for i in $initialize; do
        logger -t "LTE_Z" $i
		eval COMMAND="$i" gcom -d "$device" -s /etc/gcom/runcommand.gcom || {
			echo "Failed to initialize modem"
			proto_notify_error "$interface" INITIALIZE_FAILED
			return 1
		}
	done

	json_get_vars connect
    logger -t "LTE_Z" $connect
	eval COMMAND="$connect" gcom -d "$device" -s /etc/gcom/runcommand.gcom || {
		echo "Failed to connect"
		proto_notify_error "$interface" CONNECT_FAILED
		return 1
	}

	echo "Connected, starting DHCP"
	
	proto_init_update "$ifname" 1
	proto_send_update "$interface"

	json_init
	json_add_string name "${interface}_4"
	json_add_string ifname "@$interface"
	json_add_string proto "dhcp"
	ubus call network add_dynamic "$(json_dump)"

	json_init
	json_add_string name "${interface}_6"
	json_add_string ifname "@$interface"
	json_add_string proto "dhcpv6"
	ubus call network add_dynamic "$(json_dump)"
}

proto_inno_cdc_teardown() {
	local interface="$1"

	local manufacturer disconnect

	local device
	json_get_vars device

	echo "Stopping network"

	manufacturer='innofidei'

	json_load "$(cat /etc/gcom/inno_cdc.json)"
	json_select "$manufacturer" || {
		echo "Unsupported modem"
		proto_notify_error "$interface" UNSUPPORTED_MODEM
		return 1
	}

	json_get_vars disconnect
	eval COMMAND="$disconnect" gcom -d "$device" -s /etc/gcom/runcommand.gcom || {
		echo "Failed to disconnect"
		proto_notify_error "$interface" DISCONNECT_FAILED
		return 1
	}

	proto_init_update "*" 0
	proto_send_update "$interface"
}
[ -n "$INCLUDE_ONLY" ] || {
	add_protocol inno_cdc
}
