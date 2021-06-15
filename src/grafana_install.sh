#!/bin/sh

sudo apt-get update
sudo apt-get upgrade
sudo wget -q -o https://packages.grafana.com/gpg.key | apt-key add -
sudo apt-key list
sudo apt-get update
sudo apt-get install grafana
