#!/bin/bash

export CHECKPOINT_DISABLE=1
export DEBIAN_FRONTEND=noninteractive

set -e
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get clean
