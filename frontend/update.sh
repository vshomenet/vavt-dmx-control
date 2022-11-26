#!/bin/bash
sleep 5
/bin/systemctl stop dmx-telegram
/bin/systemctl stop dmx-sender
/bin/systemctl stop dmx-sys
cd /opt/dmx/conf
rm sys.conf
rm error_inet.conf
rm error_back.conf
rm error_sys.conf
/usr/bin/tar -cvf /tmp/dmx_backup.tar *
cd /opt
rm -rf /opt/dmx
mkdir -p /opt/dmx
cp -r /tmp/dmx/frontend/* /opt/dmx
cd /opt/dmx/conf
/usr/bin/tar -xvf /tmp/dmx_backup.tar
rm /tmp/dmx_backup.tar
rm /dev/shm/sys.conf
/bin/systemctl start dmx-sender
/bin/systemctl start dmx-sys
/bin/systemctl start dmx-telegram
/bin/systemctl restart dmx
