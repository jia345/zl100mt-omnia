#!/bin/bash

line=''

at_cmds=(
    ""
    "AT+SYSINFO"
    "AT+CPIN?"
    "AT+SNR?"
    "AT+COPS?"
    "AT+CIMI"
    "AT+CSQ"
    "AT+CGPDNS=1"
    "AT+CGPADDR=1"
    "AT+CBAND?"
)

#ParameterNum valueName Get1stParameter(expression) needCheck(0-No,1-eq,2-!eq,3-eg,4-lt) CompareData  2ndValueName Get2ndParameter 2ndNeedCheck 2ndCompareData 3rdValueName Get3rdParameter ....
cmd_data=(
	'1;connection_status;echo ${line#*:}|cut -d, -f1;0'
	'1;sim_status;echo ${line#*:};0'
	'1;snr;echo ${line#*:};0'
	'1;plmn;echo ${line#*:}|cut -d, -f3;0'
	'1;imsi;echo ${line#*:};0'
	'1;signal_strength;echo ${line#*:}|cut -d, -f1;0;0'
	'2;dns1;echo ${line#*:}|cut -d, -f2;0;0;dns2;echo ${line#*:}|cut -d, -f3;0;0'
	'1;ipaddr;echo ${line#*:}|cut -d, -f2;0;0'
	'1;band;echo ${line#*:}|cut -d, -f1;0'
)

#file='tmp.txt'
file='/root/sp4gInfo.txt'

get_4g_info(){
    rm -f $file
    sleep 0
    timeout -t 12 cat /dev/ttyUSB9 1>>$file &
    #microcom -X -t 11000 /dev/ttyUSB9 >$file &
    for cmd in ${at_cmds[@]}
        do
            #echo -e $cmd"\r\n"
            echo -e $cmd"\r\n" > /dev/ttyUSB9
            sleep 0.5 
            #echo -e $cmd"\r\n" > /dev/ttyUSB9 | timeout -t 1 cat /dev/ttyUSB9 >>$file
	done

    #sleep 3 
	#cat $file | tr -d '\r' > $file
    #echo "get 4g info done"
}

get_4g_data(){
    let state=0
    let in_cmd=1
    let cmd_end=0 
	let cmd_index=0
	data=''
    while read line
    do
        line=$(echo $line|tr -d '\r')
		if [[ $line =~ "OK" ]]
		then
			state=$cmd_end
	    	continue
		fi
        if [[ $line =~ "ERROR" ]]
		then
			state=$cmd_end
	    	continue
		fi
		if [ ${#line} -lt 2 ]
		then
		    continue
		fi
	
		#echo "line: "$line
		if [ $state -eq $cmd_end ]
		then
			i=0
		    for cmd in ${at_cmds[@]}
		    do
				#echo $cmd" | "$line
				if [[ $line == *$cmd* ]]
				then
				    state=$in_cmd
					#echo "find cmd("$i"):"$cmd
					cmd_index=$i
					break
				fi
				let i++
			done
		elif [ $state -eq $in_cmd ]
		then
			parameterNum=$(echo ${cmd_data[$cmd_index]}|cut -d\; -f1)
			#echo $parameterNum
		    for ((num=0; num<parameterNum; num++))
			do
				let parameterIndex=2+$num*4
			    ValueName=$(echo ${cmd_data[$cmd_index]}|cut -d\; -f$parameterIndex)
				let parameterIndex=3+4*$num
			    cmd_str=$(echo ${cmd_data[$cmd_index]}|cut -d\; -f$parameterIndex)
				#echo "shell cmd:"$cmd_str
				value=$(eval $cmd_str)
				#echo "value:"$value
				tmp='"'$ValueName'":"'$value'",'
				#echo "parameter($num):"$tmp 
                if [[ $value == '"'*'"' ]]
                then
				    data='"'$ValueName'":'$value','$data
                else 
				    data='"'$ValueName'":"'$value'",'$data
                fi
				#echo $data
				let parameterIndex=4+4*$num
				needcheck=$(echo ${cmd_data[$cmd_index]}|cut -d\; -f$parameterIndex)
				let parameterIndex=5+4*$num
				compare=$(echo ${cmd_data[$cmd_index]}|cut -d\; -f$parameterIndex)
				if [ $needcheck == 1 ]
				then
					#echo "need to check:"$cmd_str 
					if [[ $value == $compare ]]
					then
				    	break	
					fi
				fi
			done	
		fi

    done < $file
	echo $data
    #echo 'get sp 4g data'
}


#echo "start get 4g state"
#get_4g_info
#get_4g_data

case "$1" in
   hw)
       get_4g_info
       ;;
   sw)
       get_4g_data 
       ;;
   all)
       get_4g_info
       get_4g_data
       ;;
esac
