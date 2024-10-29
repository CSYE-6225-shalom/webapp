#!/bin/bash

set -e

sudo cp -r /tmp/app /opt/webapp/app
sudo cp /tmp/requirements.txt /opt/webapp/requirements.txt
sudo cp /tmp/webapp-systemd.service /etc/systemd/system/webapp-systemd.service
sudo cp /tmp/cloudwatch-config.json /opt/cloudwatch-config.json

# create a log directory for the 'webapp' in /var/log/ directory
sudo mkdir /var/log/webapp

# change the ownership of the directories to the user 'csye622
sudo chown -R csye6225:csye6225 /opt/webapp
sudo chown -R csye6225:csye6225 /var/log/webapp
sudo chmod 750 /var/log/webapp

sudo apt install python3 python3-pip -y
sudo apt install python3.12-venv -y 

# faced errors while installing requirements.txt file libraries and modules. 
# break-system-packages used cause no virtual environment was used
# ignore-installed flags seemed to have fixed all issues
sudo pip install -r /opt/webapp/requirements.txt --break-system-packages --ignore-installed 

sudo systemctl daemon-reload
sudo systemctl enable webapp-systemd.service
sudo systemctl start webapp-systemd.service

# After creating or modifying a service file, use daemon-reload.
# Then enable the service if you want it to start automatically on boot.
# Finally, start the service if you want it to run right away.
