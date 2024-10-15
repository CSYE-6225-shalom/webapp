#!/bin/bash

set -e

DIR="/opt/webapp"
sudo mkdir -p "$DIR"

# Create a local user with the primary group csye6225 and set the login shell to /usr/sbin/nologin
sudo groupadd csye6225
sudo useradd -g csye6225 -s /usr/sbin/nologin csye6225

# Change the ownership of the webapp folder to the user csye6225 and group csye6225
sudo chown csye6225:csye6225 /opt/webapp

# Change the permissions of the webapp folder to 755
sudo chmod 755 /opt/webapp
