#!/bin/bash
cd /opt/dmx/conf
rm sys.conf
/usr/bin/tar -cvf /tmp/dmx_backup.tar *
cd /opt
/bin/systemctl stop nginx
/bin/systemctl stop dmx
rm -rf /opt/dmx
mkdir -p /opt/dmx
cp -r /tmp/dmx/frontend/* /opt/dmx
cd /opt/dmx/conf
/usr/bin/tar -xvf /tmp/dmx_backup.tar
rm /tmp/dmx_backup.tar
/bin/systemctl start dmx
/bin/systemctl start nginx
rm -rf /tmp/dmx
