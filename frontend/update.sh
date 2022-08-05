#!/bin/bash
sleep 5
cd /opt/dmx/conf
rm sys.conf
/usr/bin/tar -cvf /tmp/dmx_backup.tar *
cd /opt
rm -rf /opt/dmx
mkdir -p /opt/dmx
cp -r /tmp/dmx/frontend/* /opt/dmx
cd /opt/dmx/conf
/usr/bin/tar -xvf /tmp/dmx_backup.tar
rm /tmp/dmx_backup.tar
/bin/systemctl restart dmx
