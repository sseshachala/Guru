#!/bin/bash

# Stop and disable the services
sudo systemctl stop celery
sudo systemctl disable celery
sudo systemctl stop gunicorn
sudo systemctl disable gunicorn
sudo systemctl stop redis-server
sudo systemctl disable redis-server
sudo systemctl stop prometheus
sudo systemctl disable prometheus
sudo systemctl stop snap.grafana.grafana
sudo systemctl disable snap.grafana.grafana

# Remove the systemd service files
sudo rm /etc/systemd/system/celery.service
sudo rm /etc/systemd/system/gunicorn.service
sudo rm /etc/systemd/system/redis.service
sudo rm /etc/systemd/system/prometheus.service

# Reload systemd to apply the changes
sudo systemctl daemon-reload

# Uninstall Redis
sudo apt-get purge --auto-remove -y redis-server

# Uninstall PostgreSQL
# sudo apt-get purge --auto-remove -y postgresql postgresql-contrib

# Remove the project directory
PROJECT_DIR=/opt/your_project_directory
sudo rm -rf $PROJECT_DIR

# Remove Celery log directory
sudo rm -rf /var/log/celery

# Remove Prometheus user and directories
sudo userdel prometheus
sudo rm -rf /etc/prometheus
sudo rm -rf /var/lib/prometheus
sudo rm /usr/local/bin/prometheus
sudo rm /usr/local/bin/promtool

# Uninstall Prometheus (if any other files/directories are missed)
sudo rm -rf /etc/systemd/system/prometheus.service
sudo rm -rf /var/lib/prometheus
sudo rm -rf /etc/prometheus

# Uninstall Grafana (installed via Snap)
sudo snap remove grafana

# Remove the Python virtual environment tools (optional)
sudo apt-get purge --auto-remove -y python3 python3-venv python3-pip

# Clean up any residual configuration files and package caches
sudo apt-get autoremove -y
sudo apt-get clean

# Confirmation message
echo "Uninstallation and cleanup complete!"
