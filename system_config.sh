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

echo "User setup completed successfully! You can now log in as $USERNAME using your SSH key."


