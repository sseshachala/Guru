To ensure the stability and availability of your application, you can use process management tools like `systemd` for managing services on Linux systems, specifically for Redis, Celery, and your FastAPI application. Additionally, you can set up monitoring and alerting to ensure you are notified if any service goes down.

### Setting Up Systemd Services

Below are the steps to create `systemd` service files for Redis, Celery, and FastAPI (Gunicorn) to ensure they automatically restart on failure.

#### 1. Create a Systemd Service for Redis

Redis typically already has a `systemd` service setup when installed via package managers like `apt`. However, here’s a quick check and how to enable it:

```sh
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

If Redis is not installed or managed by `systemd`, you can create a service file:

**/etc/systemd/system/redis.service**

```ini
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
```

Enable and start the Redis service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable redis
sudo systemctl start redis
```

#### 2. Create a Systemd Service for Celery

**/etc/systemd/system/celery.service**

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=root
Group=www-data
WorkingDirectory=/opt/your_project_directory
ExecStart=/opt/your_project_directory/venv/bin/celery -A celery_app.celery_app worker --loglevel=info --pidfile=/var/run/celery/celery.pid
PIDFile=/var/run/celery/celery.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

Ensure the working directory and paths match your project structure.

Enable and start the Celery service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl start celery
```

#### 3. Create a Systemd Service for FastAPI (Gunicorn)

**/etc/systemd/system/gunicorn.service**

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/opt/your_project_directory
ExecStart=/opt/your_project_directory/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the Gunicorn service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

### Setting Up Monitoring and Alerts

1. **Install Monitoring Tools**: Use tools like Prometheus and Grafana for monitoring, and integrate them with alerting tools like Alertmanager.
2. **Setup Alerts**: Configure alerts for service downtime, high memory usage, and other critical metrics.

### Example: Setting Up Monitoring with Prometheus and Grafana

1. **Install Prometheus**:
   ```sh
   sudo apt update
   sudo apt install prometheus -y
   ```

2. **Install Grafana**:
   ```sh
   sudo apt install -y software-properties-common
   sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
   sudo apt update
   sudo apt install grafana -y
   ```

3. **Start and Enable Grafana**:
   ```sh
   sudo systemctl start grafana-server
   sudo systemctl enable grafana-server
   ```

4. **Configure Prometheus to Scrape Metrics**:
   Edit the Prometheus configuration file (usually located at `/etc/prometheus/prometheus.yml`) to scrape metrics from your services.

5. **Set Up Alertmanager**: Integrate Prometheus with Alertmanager to handle alerts and notifications.

### Recap

1. **Systemd Service Management**: Create and manage systemd service files for Redis, Celery, and FastAPI (Gunicorn).
2. **Automatic Restarts**: Configure services to automatically restart on failure.
3. **Monitoring and Alerts**: Set up monitoring with Prometheus and Grafana, and configure alerts with Alertmanager.

By following these steps, you can ensure that your services are robust, self-healing, and monitored, providing high availability and reliability for your production environment.