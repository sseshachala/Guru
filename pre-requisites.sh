#!/bin/bash

# This script installs the prerequisites for the project and sets up the environment.

# Usage: ./pre-req.sh <requirements_file>

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <requirements_file>"
    exit 1
fi

REQUIREMENTS_FILE=$1

# Function to prompt for input and default value
if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Prompt for user input
read -p "Enter the user to run redis/celery/gunicorn: " USER
read -p "Enter the group to run redis/celery/gunicorn: " GROUP
read -p "Enter the working directory (full path): " WORKING_DIR

# Install Python 3.10 and related packages
sudo apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Create virtual environment
python3.10 -m venv $WORKING_DIR/venv
source $WORKING_DIR/venv/bin/activate

# Install pip for Python 3.10
curl https://bootstrap.pypa.io/get-pip.py | python3.10
pip install --upgrade pip

# Install requirements from requirements.txt
pip install -r $REQUIREMENTS_FILE

# Add ~/.local/bin to PATH in .profile if not already present
if ! grep -q "PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.profile; then
    echo -e "\n# set PATH so it includes user's private bin if it exists" >> ~/.profile
    echo 'if [ -d "$HOME/.local/bin" ] ; then' >> ~/.profile
    echo '    PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
    echo 'fi' >> ~/.profile
    echo "Added ~/.local/bin to PATH in .profile"
else
    echo "~/.local/bin already in PATH in .profile"
fi

# Add virtual environment bin to PATH
echo "PATH=\"$WORKING_DIR/venv/bin:\$PATH\"" >> ~/.profile
source ~/.profile

# Create ~/.local/bin if it doesn't exist
mkdir -p ~/.local/bin

# Install and configure Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure Redis for persistence
sudo tee -a /etc/redis/redis.conf <<EOF
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfilename "appendonly.aof"
EOF
sudo systemctl restart redis-server

# Install Celery
pip install celery

# Ensure CELERY_APP points to the correct module
CELERY_APP="celery_app" # Since celery_app.py is in the WORKING_DIR

# Create systemd service file for Celery
cat << EOF > /etc/systemd/system/celery.service
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=$USER
Group=$GROUP
EnvironmentFile=/etc/default/celeryd
WorkingDirectory=$WORKING_DIR
ExecStart=$WORKING_DIR/venv/bin/celery multi start worker1 \\
  -A $CELERY_APP --pidfile=/var/run/celery/%n.pid \\
  --logfile=/var/log/celery/%n.log --loglevel=INFO
ExecStop=$WORKING_DIR/venv/bin/celery multi stopwait worker1 \\
  --pidfile=/var/run/celery/%n.pid
ExecReload=$WORKING_DIR/venv/bin/celery multi restart worker1 \\
  -A $CELERY_APP --pidfile=/var/run/celery/%n.pid \\
  --logfile=/var/log/celery/%n.log --loglevel=INFO

[Install]
WantedBy=multi-user.target
EOF

# Create necessary directories
mkdir -p /var/log/celery /var/run/celery
chown $USER:$GROUP /var/log/celery /var/run/celery

# Create configuration file for Celery
cat << EOF > /etc/default/celeryd
# Names of nodes to start
CELERYD_NODES="worker1"

# App instance to use
CELERY_APP="$CELERY_APP"

# Where to chdir at start.
CELERYD_CHDIR="$WORKING_DIR"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %n will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%n.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

# Workers should run as an unprivileged user.
CELERYD_USER="$USER"
CELERYD_GROUP="$GROUP"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1
EOF

# Reload systemd, enable and start the Celery service
sudo systemctl daemon-reload
sudo systemctl enable celery.service
sudo systemctl start celery.service

echo "Celery service has been set up and started."
echo "You can check its status with: systemctl status celery.service"

# Install Gunicorn
pip install gunicorn

# Find the full path to Gunicorn
GUNICORN_PATH=$(which gunicorn)

# Create log directory
LOG_DIR="/var/log/app_main"
mkdir -p $LOG_DIR
chown $USER:$GROUP $LOG_DIR

# Create the systemd service file for the FastAPI app with Gunicorn
cat << EOF > /etc/systemd/system/app.main.service
[Unit]
Description=FastAPI app.main with Gunicorn
After=network.target

[Service]
User=$USER
Group=$GROUP
WorkingDirectory=$WORKING_DIR
ExecStart=$GUNICORN_PATH app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --access-logfile $LOG_DIR/access.log --error-logfile $LOG_DIR/error.log
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the FastAPI service
sudo systemctl daemon-reload
sudo systemctl enable app.main
sudo systemctl start app.main

echo "app.main service has been created and started."
echo "You can check the status with: systemctl status app.main"
echo "Access logs are in $LOG_DIR/access.log"
echo "Error logs are in $LOG_DIR/error.log"

# Configure firewall to open necessary ports
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 8000
sudo ufw enable

echo "Firewall has been configured to allow ports 22, 80, and 8000."

# Check Redis status
# sudo systemctl status redis-server
# redis-cli ping

# Check Celery status
# sudo systemctl status celery.service
# ps aux | grep 'celery worker'

# Check Gunicorn status
# sudo systemctl status app.main
# ps aux | grep gunicorn

