#!/bin/sh
# install required system packages
sudo apt-get update
sudo apt-get install -y \
  libftdi-dev \
  python3-pip \
  python3-pil \
  python3-numpy \
  python3-virtualenv

# create/recreate virtualenv
rm -rf venv
virtualenv -p python3 venv
./venv/bin/activate
./venv/bin/pip install -r requirements.txt
