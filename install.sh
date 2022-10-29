#!/bin/bash
echo "Start install"
echo "Install software..."
apt-get update -y && apt-get upgrade -y && apt-get install -y python3 python3-pip git nginx libpcre3 libpcre3-dev #uwsgi uwsgi-plugin-python3
echo "Install python modules..."
pip3 install Flask Flask-WTF WTForm Jinja2 uwsgi pyserial dmx485 aiogram
echo "Start config system..."
mkdir -p /opt/dmx
cp -r frontend/* /opt/dmx
sleep 5
echo "Start config uWSGI..."
cp sys-conf/dmx.service /etc/systemd/system
/bin/systemctl enable dmx
/bin/systemctl restart dmx
sleep 5
echo "Start config nginx..."
cp sys-conf/nginx.conf /etc/nginx
cp sys-conf/web-dmx /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/web-dmx /etc/nginx/sites-enabled
rm /etc/nginx/sites-enabled/default
/bin/systemctl restart nginx
sleep 5
echo "Start config DMX - sender..."
cp sys-conf/dmx-sender.service /etc/systemd/system
/bin/systemctl enable dmx-sender
/bin/systemctl restart dmx-sender
sleep 5
echo "Start config DMX - system monitor..."
cp sys-conf/dmx-sys.service /etc/systemd/system
/bin/systemctl enable dmx-sys
/bin/systemctl restart dmx-sys
sleep 5
echo "Start config password for system..."
sleep 5
echo
echo
/opt/dmx/reset_pass.py

