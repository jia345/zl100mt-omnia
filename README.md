# ZL100MT-SW
机载融合交换机 - ZL100MT空地宽带链路系统

# booting from UART

```
sudo ./kwboot -t -B 115200 /dev/ttyUSB0 -b uboot-turris-omnia-uart-spl.kwb
```

# commands to burn NOR flash
## - on host Linux
```
mkdir /mnt/ssd
sudo fdisk /dev/sdb
sudo mkfs.btrfs /dev/sdb1
sudo mount /dev/sdb /mnt/ssd
sudo btrfs subvol create /mnt/ssd/@
sudo cp uboot-turris-omnia-spl.kwb /mnt/ssd/
```
## - on target after booting using kwboot by UART
```
btrload mmc 0 0x2000000 uboot-turris-omnia-spl.kwb
sf erase 0 0x200000
sf write 0x2000000 0 $filesize
```

# commands to setup development environment
```
git clone https://github.com/CZ-NIC/turris-os.git zl100mt-os
sudo apt-get update
sudo apt-get install lxc
wget https://releases.hashicorp.com/vagrant/2.2.2/vagrant_2.2.2_x86_64.deb
sudo dpkg -i vagrant_2.2.2_x86_64.deb
vagrant plugin install vagrant-lxc
cd zl100mt-os
ln -s vagrant/Vagrantfile
vagrant up --provider=lxc
vagrant ssh
sudo apt install python-dev
BUILD_ALL=y ./compile_omnia_fw IGNORE_ERRORS=m 2>&1 | tee build.log
```

# commands to start you development
```
cd zl100mt-os
vagrant ssh
...your work...
```

