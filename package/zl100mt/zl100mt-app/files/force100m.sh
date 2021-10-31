#!/bin/sh

function force_100m(){
    swconfig dev switch0 port 1 set link "autoneg on"
    sleep 1
    swconfig dev switch0 port 1 set link "duplex full speed 10 autoneg off"
    sleep 3
    swconfig dev switch0 port 1 set link "duplex full speed 100 autoneg off"
    sleep 1
    
    swconfig dev switch0 port 2 set link "autoneg on"
    sleep 1
    swconfig dev switch0 port 2 set link "duplex full speed 10 autoneg off"
    sleep 3
    swconfig dev switch0 port 2 set link "duplex full speed 100 autoneg off"
    sleep 1
    
    swconfig dev switch0 port 3 set link "autoneg on"
    sleep 1
    swconfig dev switch0 port 3 set link "duplex full speed 10 autoneg off"
    sleep 3
    swconfig dev switch0 port 3 set link "duplex full speed 100 autoneg off"
    sleep 1
}

function autoneg(){
    swconfig dev switch0 port 1 set link "autoneg on"
    sleep 1
    swconfig dev switch0 port 2 set link "autoneg on"
    sleep 1
    swconfig dev switch0 port 3 set link "autoneg on"
    sleep 1
}

case "$1" in
    on)
      force_100m
    ;;
    off)
      autoneg
    ;;
esac
