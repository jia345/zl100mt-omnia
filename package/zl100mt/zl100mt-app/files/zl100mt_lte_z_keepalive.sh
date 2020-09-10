#!/bin/sh

mutex_file=/tmp/restart_lte_z

lte_z_result=`ip addr show dev eth2|grep "inet "`
if [ $? -eq 1 ]
then
    [ ! -f $mutex_file ] && {
        logger -t "LTE_Z" "network is down, reconnecting..."
        touch $mutex_file
        ifup lte_z
        sleep 10
        rm $mutex_file
    }
fi

