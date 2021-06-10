#!/bin/sh

echo "influxdb installing..."
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.7.8_amd64.deb
sudo dpkg -i influxdb_1.7.8_amd64.deb

sudo systemctl enable --now influxdb

sudo apt upgrade
