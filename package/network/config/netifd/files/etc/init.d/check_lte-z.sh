#!/bin/sh

# Enter the FQDNs(fully qualified domain name) you want to check with ping (space separated)
# Script does nothing if any tries to any FQDN succeeds
FQDN="www.toutiao.com"
FQDN="$FQDN www.taobao.com"
FQDN="$FQDN www.qq.com"

# Sleep between ping checks of a FQDN (seconds between pings)
SLEEP=3                         # Sleep time between each retry
RETRY=3                         # Retry each FQDN $RETRY times
SLEEP_MAIN=20                   # Main loop sleep time

check_connection()
{
  for NAME in $FQDN; do
    for i in $(seq 1 $RETRY); do
      ping -c 1 $NAME > /dev/null 2>&1
      if [ $? -eq 0 ]; then
        return 0
      fi
      sleep $SLEEP
    done
  done
  # If we are here, it means all failed
  return 1
}

while true; do
  check_connection
  if [ $? -ne 0 ]; then
    /etc/init.d/lte-z restart
  fi
  sleep $SLEEP_MAIN
done
