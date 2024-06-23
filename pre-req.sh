#!/bin/bash

# This script installs the prerequisites for the project.

# ./pre-req.sh <requirements_file>

# Check if the requirements file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <requirements_file>"
    exit 1
fi

REQUIREMENTS_FILE=$1

# 4. Install Python 3.12
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# 5. Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 6. Install requirements from requirements.txt
sudo apt install -y python3-pip
pip3 install --user -r $REQUIREMENTS_FILE

echo "Python, PostgreSQL, and requirements installation completed successfully!"