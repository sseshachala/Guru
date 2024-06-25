#!/bin/bash

# This script installs the prerequisites for the project.

# Usage: ./pre-req.sh <requirements_file> <db_name> <db_user> <db_password>

# This script sets up a new user with sudo privileges and a public SSH key.
# chmod +x pre-req.sh

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <requirements_file> <db_name> <db_user> <db_password>"
    exit 1
fi

REQUIREMENTS_FILE=$1
# DB_NAME=$2
# DB_USER=$3
# DB_PASSWORD=$4

# 4. Install Python 3.12
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo apt install alembic

# 5. Install PostgreSQL
# sudo apt install -y postgresql postgresql-contrib

# 6. Install requirements from requirements.txt
# sudo apt install -y python3-pip
pip3.12 install --user -r $REQUIREMENTS_FILE

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

source ~/.profile

# 8. Create ~/.local/bin if it doesn't exist
mkdir -p ~/.local/bin

# 9. Set up PostgreSQL user and database
# sudo -i -u postgres psql <<EOF
-- Create a new PostgreSQL user
 # CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create a new PostgreSQL database
# CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant all privileges on the database to the new user
# GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Exit the PostgreSQL prompt
# EOF

# echo "PostgreSQL setup completed: user '$DB_USER' with database '$DB_NAME' has been created."

# echo "Python, PostgreSQL, and requirements installation completed successfully!"
echo "~/.local/bin has been added to your PATH. Please log out and log back in, or run 'source ~/.profile' to apply the changes."
