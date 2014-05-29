#!/bin/bash
d=$(fdisk -l /dev/sd? |grep -E -o "/dev/sd[a-z][0-9]+")
mount -t vfat $d /mnt/usb_hd/
python /mnt/usb_hd/program.py > /mnt/usb_hd/output.txt 2> /mnt/usb_hd/error.txt
umount $d