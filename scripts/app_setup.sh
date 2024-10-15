#!/bin/bash

set -e

sudo cp -r /tmp/app /opt/webapp/app
sudo cp /tmp/.env /opt/webapp/.env
sudo cp /tmp/requirements.txt /opt/webapp/requirements.txt
sudo cp /tmp/webapp-systemd.service /etc/systemd/system/webapp-systemd.service

sudo chown -R csye6225:csye6225 /opt/webapp

# Source the .env file
source /opt/webapp/.env

sudo apt install python3 python3-pip -y
sudo apt install postgresql postgresql-contrib -y 
sudo apt install python3.12-venv -y 

sudo pip install -r /opt/webapp/requirements.txt --break-system-packages --ignore-installed 

sudo -u postgres psql << EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER USER $DB_USER WITH SUPERUSER;
EOF

sudo systemctl daemon-reload
sudo systemctl enable webapp-systemd.service
sudo systemctl start webapp-systemd.service
