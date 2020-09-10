#!/bin/sh

mutex_file=/tmp/restart_lte_4g

lte_4g_result=`ip addr show dev usb0|grep "inet "`
if [ $? -eq 1 ]
then
    [ ! -f $mutex_file ] && {
        logger -t "LTE_4G" "network is down, reconnecting..."
        touch $mutex_file
        ifup lte_4g
        sleep 10
        rm $mutex_file
    }
fi

