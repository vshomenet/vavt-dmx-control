#!/bin/bash
echo "Start install"
echo "Install software..."
#apt-get update -y && apt-get upgrade -y && apt-get install -y python3 python3-pip git nginx
echo "Install python modules..."
#pip3 install Flask Flask-WTF WTForm Jinja2
echo "Start config system..."
mkdir -p /opt/dmx && mkdir -p /opt/dmx/update
cp -r frontend/* /opt/dmx
echo 
/opt/dmx/reset_pass.py
