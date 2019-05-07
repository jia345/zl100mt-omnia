#!/bin/sh

get_temp() {
  resolution=0.0625
  
  byte1=`i2cget -y 0 0x48 0`
  byte2=`i2cget -y 0 0x48 1`
  
  digi=$(((byte1<<4) | (byte2>>4)))
  
  is_negative=$((digi & 0x800))
  
  if [ 0 != $is_negative ] ; then
    digi=$((~digi+1))
  fi
  
  temp=`echo "$digi * $resolution" | bc`
  rc=`printf "%.2f" $temp`
  echo $rc
}

temp=$(get_temp)

logger -t tmp112 -p info "current TEMPERATURE is: $temp degrees Celsius"

