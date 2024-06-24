Understood. Here's the revised script to only include Redis, Celery, Prometheus, Grafana, and the FastAPI application. RabbitMQ is removed from the script.

```sh
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
pip install celery[redis] gunicorn uvicorn psycopg2-binary fastapi

# Sample FastAPI application setup
mkdir -p $PROJECT_DIR/app
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
    broker="redis://localhost:6379/0"
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

# End of script
```

### Usage Instructions

1. **Save the Script**: Save the script as `setup.sh` on your server.
2. **Make the Script Executable**: Run `chmod +x setup.sh` to make the script executable.
3. **Execute the Script**: Run `./setup.sh` to execute the script and provide the PostgreSQL database details when prompted.

This updated script will:
1. **Prompt for PostgreSQL database details**.
2. **Install Redis, PostgreSQL, Prometheus, and Grafana**.
3. **Configure Redis for persistence**.
4. **Set up a Python virtual environment and install necessary Python packages**.
5. **Create a sample FastAPI application and a Celery worker**.
6. **Create and configure systemd service files for Redis, Celery, FastAPI (Gunicorn), and Prometheus**.
7. **Start and enable the services, with error handling for Celery**.
8. **Install Grafana using Snap and enable it**.
9. **Output the URLs for accessing Prometheus and Grafana**.