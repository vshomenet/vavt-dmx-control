#!/bin/bash
cd conf
rm sys.conf
/usr/bin/tar -cvf /tmp/dmx_backup.tar *
/bin/systemctl stop nginx
/bin/systemctl stop dmx
rm -rf /opt/dmx
mkdir -p /opt/dmx
cp -r frontend/* /opt/dmx

/bin/systemctl start dmx
/bin/systemctl start nginx
