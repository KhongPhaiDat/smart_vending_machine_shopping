#!/bin/bash

# Update the package manager and install necessary packages
sudo yum update -y
sudo yum install -y git python3-pip

# Change into ec2-user directory
cd /home/ec2-user
# Clone the Git repository
sudo -u ec2-user git clone https://github.com/KhongPhaiDat/smart_vending_machine_shopping.git

# Change into the repository directory
cd smart_vending_machine_shopping

# Install Python dependencies using pip
sudo -u ec2-user pip3 install -r requirements.txt

# Copy the systemd service file to the appropriate location
sudo cp scripts/streamlit_app.service /etc/systemd/system/

# Reload systemd to pick up the new service file
sudo systemctl daemon-reload

# Start the service
sudo systemctl start streamlit_app

# Enable the service to start on boot
sudo systemctl enable streamlit_app