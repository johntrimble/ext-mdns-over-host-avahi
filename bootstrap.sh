#!/usr/bin/env bash

apt-get update -y
apt-get upgrade -y
apt-get install -y libnss-mdns avahi-daemon python3 avahi-utils python3-pydbus
