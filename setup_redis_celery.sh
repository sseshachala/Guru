#!/bin/bash

# Function to prompt for input and default value
prompt() {
    read -p "$1 [$2]: " input
    echo "${input:-$2}"
}

# Prompt for PostgreSQL database details
db_name=$(prompt "Enter PostgreSQL database name" "celerydb")
db_user=$(prompt "Enter PostgreSQL database user" "celeryuser")
db_password=$(prompt "Enter PostgreSQL database password" "celerypassword")

# Update and upgrade the system
sudo apt update && sudo apt upgrade -y

# Install Redis
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


# Systemd service files

# Redis service file (if not already present)
cat <<EOF | sudo tee /etc/systemd/system/redis.service
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/bin/redis-cli shutdown
Restart=always
User=redis
Group=redis

[Install]
WantedBy=multi-user.target
EOF

# Celery service file
cat <<EOF | sudo tee /etc/systemd/system/celery.service
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=$USER
Group=www-data
ExecStart=celery -A celery_app.celery_app worker --loglevel=info --pidfile=/var/run/celery/celery.pid --logfile=/var/log/celery/celery.log
PIDFile=/var/run/celery/celery.pid
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Gunicorn service file
cat <<EOF | sudo tee /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl start celery || (echo "Failed to start celery service. See 'systemctl status celery.service' and 'journalctl -xeu celery.service' for details." && exit 1)
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Install Prometheus
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus

cd /tmp
curl -LO https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz
cd prometheus-2.40.0.linux-amd64

sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool

sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus
sudo cp prometheus.yml /etc/prometheus/prometheus.yml
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml

# Prometheus service file
cat <<EOF | sudo tee /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \\
    --config.file /etc/prometheus/prometheus.yml \\
    --storage.tsdb.path /var/lib/prometheus/ \\
    --web.console.templates=/etc/prometheus/consoles \\
    --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus

# Install Grafana using Snap
sudo snap install grafana

# Start and enable Grafana
sudo systemctl start snap.grafana.grafana
sudo systemctl enable snap.grafana.grafana

# Get the server IP address
server_ip=$(hostname -I | awk '{print $1}')

# Output the access URLs
echo "Setup complete!"
echo "Access Prometheus at http://$server_ip:9090"
echo "Access Grafana at http://$server_ip:3000 (default login is admin/admin)"
echo "Ensure Prometheus and Grafana are configured to scrape metrics from your services."
echo "Configure Grafana to use Prometheus as a data source."
echo "Celery log: /var/log/celery/celery.log"

# End of script
