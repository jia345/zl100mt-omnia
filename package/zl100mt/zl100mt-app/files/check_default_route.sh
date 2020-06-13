#!/bin/bash

line=`ip addr show usb0 | grep UP`

if [ -z "$line" ]
    then
    logger "Lte 4G interface is down!"
    exit 0
fi

line=`ip addr show usb0 | grep inet`
echo $line

if [ -z "$line" ]
then
    logger "Lte 4G interface Not got ip!"
    exit 0
fi

line=`ip route list table 254 | grep default`
i=1
def_gw_ip=""
for element in $line
do
    if [ $i == 3 ]
        then
        def_gw_ip=$element
    fi
    i=`expr $i + 1`
done
logger "defautl gw ip: $def_gw_ip"

line=`ip route list table 254 | grep usb0 | grep static | grep scope`
i=1
lte_4g_ip=""
for element in $line
do
    if [ $i == 1 ]
        then
        lte_4g_ip=$element
    fi
    i=`expr $i + 1`
done
logger "4g_ip: $lte_4g_ip" 

if [ "$def_gw_ip" = "$lte_4g_ip" ]
    then
    logger "Default GW is matched!"
else
    logger "Default GW need reconfigure!"
    if [ -n "$def_gw_ip" ]; then
        cmd=`ip route del default`
    fi
    cmd=`ip route add default via $lte_4g_ip dev usb0`
fi
exit 0

