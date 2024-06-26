#!/bin/bash

# sudo ./system_config.sh develop "1yc2EAAMqpBEpRBUTKoA+6aV4/Tx4Gs/LYhXC1U5oCZ2KPoJAJtHTMKBaKlg0ICi5 ctp1126@CTPs-MBP-2"

# This script sets up a new user with sudo privileges and a public SSH key.
# chmod +x system_config.sh
# ./system_config.sh <username> "<ssh_public_key>"

# Check if all required parameters are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <username> <ssh_public_key>"
    exit 1
fi

# Assign parameters to variables
USERNAME=$1
SSH_PUBLIC_KEY=$2

# 1. Create the user
adduser --disabled-password --gecos "" $USERNAME

# 2. Add user to sudo group
usermod -aG sudo $USERNAME

# 3. Set up SSH key
mkdir -p /home/$USERNAME/.ssh
echo "$SSH_PUBLIC_KEY" | tee /home/$USERNAME/.ssh/authorized_keys
chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh
chmod 700 /home/$USERNAME/.ssh
chmod 600 /home/$USERNAME/.ssh/authorized_keys

echo "develop ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/develop
sudo chmod 440 /etc/sudoers.d/develop

echo "User setup completed successfully! You can now log in as $USERNAME using your SSH key."

# Ensure UFW is installed
if ! command -v ufw &> /dev/null
then
    echo "UFW is not installed. Installing UFW..."
    sudo apt-get update
    sudo apt-get install ufw -y
fi

# Enable UFW
echo "Enabling UFW..."
sudo ufw enable

# Allow ports 80 and 8000
echo "Allowing ports 80 and 8000..."
sudo ufw allow 80
sudo ufw allow 8000

# Reload UFW to apply changes
echo "Reloading UFW..."
sudo ufw reload

echo "Ports 80 and 8000 are now open."


