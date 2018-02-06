#!/usr/bin/env bash

set -e

echo "Drop Installer script"

echo "First installing few packages with apt-get as root"
sudo \
apt-get -y install git build-essential \
           make build-essential libssl-dev zlib1g-dev libbz2-dev \
           libreadline-dev libsqlite3-dev wget curl llvm \
           libncurses5-dev libncursesw5-dev xz-utils tk-dev python-dev \
           python-pip

echo "Installing Drop from Github with pip"
pip install https://github.com/infant-cognition-tampere/drop/archive/master.zip

echo ''
echo 'Drop should be now installed to the PATH.'
echo 'You should be now able to run drop from terminal with command "drop"'