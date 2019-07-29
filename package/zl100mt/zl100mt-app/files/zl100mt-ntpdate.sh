#!/bin/sh

. /lib/config/uci.sh

SERVER=`uci get system.ntp.server`

TIMEOUT="2" # in seconds

( for s in $STEP_SERVERS ; do
	/usr/sbin/ntpdate -s -b -u -t "$TIMEOUT" "$s" && break
  done ) &
