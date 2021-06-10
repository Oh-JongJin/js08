#!/bin/sh

echo "User name:" "$USERNAME"
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.7.8_amd64.deb
sudo dpkg -i influxdb_1.7.8_amd64.deb

sudo systemctl enable --now influxdb

sudo apt upgrade
