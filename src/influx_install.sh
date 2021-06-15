#!/bin/sh

<<<<<<< HEAD
echo "influxDB installing..."
=======
echo "influxdb installing..."
>>>>>>> c99add77805ad6e9f97cdbc2cfbbc8c06b8c95d9
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.7.8_amd64.deb
sudo dpkg -i influxdb_1.7.8_amd64.deb

sudo systemctl enable --now influxdb

sudo apt upgrade
