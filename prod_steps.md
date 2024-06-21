Building a production server for your FastAPI application involves several steps, including setting up a virtual machine (VM) or server, configuring the environment, installing dependencies, setting up a reverse proxy with Nginx, securing the application with SSL, and deploying the application with a process manager like Gunicorn and Celery for task management. Below are the consolidated steps to set up a production server on DigitalOcean, but these steps are generally applicable to other cloud providers as well.

### Step-by-Step Guide to Setting Up a Production Server

#### 1. Create and Access a Virtual Machine

1. **Create a Droplet on DigitalOcean**:
   - Log in to your DigitalOcean account.
   - Create a new Droplet with Ubuntu 20.04 LTS.
   - Choose a plan based on your needs.
   - Add your SSH key for secure access.
   - Create the Droplet.

2. **Access the Droplet**:
   ```sh
   ssh root@your_droplet_ip
   ```

#### 2. Update and Upgrade the System

```sh
sudo apt update
sudo apt upgrade -y
```

#### 3. Install Required Dependencies

1. **Install Python and pip**:
   ```sh
   sudo apt install python3 python3-pip -y
   ```

2. **Install Git**:
   ```sh
   sudo apt install git -y
   ```

3. **Install Redis**:
   ```sh
   sudo apt install redis-server -y
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```

#### 4. Clone Your Project Repository

```sh
cd /opt
git clone your_repository_url
cd your_project_directory
```

#### 5. Set Up a Virtual Environment

1. **Install virtualenv**:
   ```sh
   sudo pip3 install virtualenv
   ```

2. **Create and activate a virtual environment**:
   ```sh
   virtualenv venv
   source venv/bin/activate
   ```

3. **Install project dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

#### 6. Set Up Celery

1. **Create `celery_app.py`**:
   ```python
   from celery import Celery

   celery_app = Celery(
       "worker",
       backend="redis://localhost:6379/0",
       broker="redis://localhost:6379/0"
   )

   celery_app.conf.update(
       task_serializer="json",
       accept_content=["json"],
       result_serializer="json",
       timezone="UTC",
       enable_utc=True,
   )

   celery_app.autodiscover_tasks(['app'])
   ```

2. **Ensure `tasks.py` is correctly configured**:
   ```python
   from celery_app import celery_app
   from .utils import download_yt, transcript_yt

   @celery_app.task(name="app.tasks.process_transcript")
   def process_transcript(url):
       audio_file = download_yt(url)
       return transcript_yt(audio_file)
   ```

3. **Start the Celery worker**:
   ```sh
   export PYTHONPATH=$(pwd)
   celery -A celery_app.celery_app worker --loglevel=info
   ```

#### 7. Set Up Nginx

1. **Install Nginx**:
   ```sh
   sudo apt install nginx -y
   ```

2. **Create an Nginx configuration file**:
   ```sh
   sudo nano /etc/nginx/sites-available/your_project
   ```

3. **Add the following configuration**:
   ```nginx
   server {
       listen 80;
       server_name your_domain_or_ip;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Enable the Nginx configuration**:
   ```sh
   sudo ln -s /etc/nginx/sites-available/your_project /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### 8. Secure Your Application with SSL (Optional but Recommended)

1. **Install Certbot**:
   ```sh
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. **Obtain and install an SSL certificate**:
   ```sh
   sudo certbot --nginx -d your_domain
   ```

#### 9. Set Up Gunicorn to Serve FastAPI

1. **Install Gunicorn**:
   ```sh
   pip install gunicorn
   ```

2. **Create a Gunicorn service file**:
   ```sh
   sudo nano /etc/systemd/system/gunicorn.service
   ```

3. **Add the following configuration**:
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=root
   Group=www-data
   WorkingDirectory=/opt/your_project_directory
   ExecStart=/opt/your_project_directory/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start and enable the Gunicorn service**:
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

#### 10. Start the FastAPI Application

1. **Navigate to your project directory**:
   ```sh
   cd /opt/your_project_directory
   ```

2. **Start FastAPI with Uvicorn**:
   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

#### 11. Verify the Deployment

- Visit your domain or server IP in a web browser to verify that your FastAPI application is running.

### Summary

- **Droplet Setup**: Create and configure a DigitalOcean Droplet.
- **System Update**: Update and upgrade the system packages.
- **Dependency Installation**: Install Python, pip, Git, Redis, Nginx, Gunicorn, and Certbot.
- **Project Setup**: Clone your repository, set up a virtual environment, and install dependencies.
- **Celery Configuration**: Set up Celery for background task processing.
- **Nginx Configuration**: Configure Nginx as a reverse proxy.
- **SSL Configuration**: Secure the application with SSL using Certbot.
- **Gunicorn Configuration**: Set up Gunicorn to serve the FastAPI application.
- **Application Start**: Start the FastAPI application with Uvicorn.

By following these steps, you can set up a robust production server for your FastAPI application. If you encounter any issues or need further assistance, please let me know!