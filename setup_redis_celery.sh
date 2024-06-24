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

# Install RabbitMQ
sudo apt install -y rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql <<EOF
CREATE DATABASE $db_name;
CREATE USER $db_user WITH ENCRYPTED PASSWORD '$db_password';
GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;
EOF

# Install Python and virtual environment tools
sudo apt install -y python3 python3-venv python3-pip

# Create a project directory
PROJECT_DIR=/opt/your_project_directory
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Create a Python virtual environment and install dependencies
python3 -m venv $PROJECT_DIR/venv
source $PROJECT_DIR/venv/bin/activate
pip install celery[redis] gunicorn uvicorn psycopg2-binary

# Sample FastAPI application setup
cat > $PROJECT_DIR/app/main.py <<EOF
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
EOF

# Sample Celery configuration and task
cat > $PROJECT_DIR/celery_app.py <<EOF
from celery import Celery

celery_app = Celery(
    "worker",
    backend="db+postgresql://$db_user:$db_password@localhost/$db_name",
    broker="amqp://localhost"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def add(x, y):
    return x + y
EOF

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

# RabbitMQ service file (if not already present)
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Celery service file
cat <<EOF | sudo tee /etc/systemd/system/celery.service
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/celery -A celery_app.celery_app worker --loglevel=info --pidfile=/var/run/celery/celery.pid
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
sudo systemctl start celery
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Install Prometheus and Grafana
sudo apt install -y prometheus grafana

# Start and enable Prometheus and Grafana
sudo systemctl start prometheus
sudo systemctl enable prometheus
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Get the server IP address
server_ip=$(hostname -I | awk '{print $1}')

# Output the access URLs
echo "Setup complete!"
echo "Access Prometheus at http://$server_ip:9090"
echo "Access Grafana at http://$server_ip:3000 (default login is admin/admin)"
echo "Ensure Prometheus and Grafana are configured to scrape metrics from your services."
echo "Configure Grafana to use Prometheus as a data source."

# End of script
