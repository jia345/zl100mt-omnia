#!/bin/bash
#set -xe

REALPATH=`realpath ${0}`
PWD=`dirname ${REALPATH}`
ROOTFS=${PWD}/zl100mt-rootfs.tar.gz

if [ -f ${ROOTFS} ]; then
    echo -e "\nFind ${ROOTFS}, let's go...\n"
    # checking commands do exist, including mkfs.btrfs, fdisk, btrfs...
    commands="fdisk mkfs.btrfs btrfs udisksctl md5sum"
    for c in $commands; do
        if ! [ $(command -v ${c}) ]; then
            echo "ERROR: ${c} is required, please install it in advance, exiting..."
            exit 1
        fi
    done

    count=0
    declare -A media_list
    while read -r line; do
        ((count++))
        mount_dev=`echo $line | cut -d' ' -f1`
        mount_point=`echo $line | cut -d' ' -f3`
        media_list+=([${mount_dev}]=${mount_point})
    done < <(mount | grep media)

    #
    # menu
    #
    if [ $count -eq 0 ]; then
        echo "==================================================================="
        echo " ERROR: no any TF card found, please insert one or re-insert it in"
        echo "==================================================================="
        exit 1
    elif [ $count -gt 1 ]; then
        while :; do
            echo -e "* Choose the removable disk you are using...\n"
            i=0
            options=()
            option_ids=""
            for k in ${!media_list[@]}; do
                ((i++))
                echo -e "  $i - ${media_list[${k}]}"
                options[${i}]=${k}
                option_ids+=" $i"
            done
            echo -e "  x - quit\n"
            echo ""
            option_ids+=" x"
            read -p "  Please make a choice: " num
            #echo ${media_list[$num % ${media_list[@]}]}
            if [[ "${option_ids}" =~ "${num}" ]]; then
                if [ ${num} = 'x' ]; then
                    echo -e "\n  quit"
                    exit 1
                elif [ ! ${num}  ]; then
                    continue
                else
                    mount_dev=${options[${num}]}
                    mount_point=${media_list[${mount_dev}]}
                    break
                fi
            else
                echo -e "\n > Wrong input, please try again...\n"
            fi
        done
    fi

    echo -e "\n  CAUTION: WE WILL FORMAT $mount_dev @ $mount_point\n"

    while :; do
        read  -p "  ARE YOUR SURE? <Y/n> " YorN
        echo $YorN
        if [ ! ${YorN} ]; then
            continue
        elif [ ${YorN} = 'Y' ]; then
            break
        elif [ ${YorN} = "n" -o ${YorN} = "N" ]; then
            echo "quit"
            exit 1
        else
            echo -e "\n > Wrong input, please retry...\n"
        fi
    done

    sudo umount ${mount_point} 2>/dev/null
    sudo fdisk ${mount_dev}
    #udisksctl mount -b /dev/sdb1
    echo "done"
else
    echo -e "\nERROR: please make sure the upgrade package exists in the same directory as this script\n"
fi

