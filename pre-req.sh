#!/bin/bash

# This script installs the prerequisites for the project.

# ./pre-req.sh <requirements_file>

# This script sets up a new user with sudo privileges and a public SSH key.
# chmod +x pre-req.sh

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

# 7. Add ~/.local/bin to PATH in .profile
if ! grep -q "PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.profile; then
    echo -e "\n# set PATH so it includes user's private bin if it exists" >> ~/.profile
    echo 'if [ -d "$HOME/.local/bin" ] ; then' >> ~/.profile
    echo '    PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
    echo 'fi' >> ~/.profile
    echo "Added ~/.local/bin to PATH in .profile"
else
    echo "~/.local/bin already in PATH in .profile"
fi


# 8. Create ~/.local/bin if it doesn't exist
mkdir -p ~/.local/bin

echo "Python, PostgreSQL, and requirements installation completed successfully!"
echo "~/.local/bin has been added to your PATH. Please log out and log back in, or run 'source ~/.profile' to apply the changes."