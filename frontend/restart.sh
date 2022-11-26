#!/bin/bash
/bin/systemctl stop dmx-telegram
/bin/systemctl stop dmx-sender
/bin/systemctl stop dmx-sys
rm /dev/shm/error_inet.conf
rm /dev/shm/error_back.conf
rm /dev/shm/error_sys.conf
sleep 3
/bin/systemctl start dmx-sender
/bin/systemctl start dmx-sys
/bin/systemctl start dmx-telegram
/bin/systemctl restart dmx
