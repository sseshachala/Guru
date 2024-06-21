To run Redis and Celery, follow these steps. We'll start Redis, then start the Celery worker, and finally start the FastAPI application.

### Step 1: Start Redis

#### On Ubuntu

1. **Install Redis (if not already installed)**:
    ```sh
    sudo apt update
    sudo apt install redis-server -y
    ```

2. **Start Redis**:
    ```sh
    sudo systemctl start redis-server
    ```

3. **Enable Redis to start on boot**:
    ```sh
    sudo systemctl enable redis-server
    ```

#### On macOS

1. **Install Redis (if not already installed, using Homebrew)**:
    ```sh
    brew install redis
    ```

2. **Start Redis**:
    ```sh
    redis-server /usr/local/etc/redis.conf
    ```

### Step 2: Start the Celery Worker

Navigate to your project directory and ensure your Python environment is activated. Then, run the following commands:

1. **Set the Python path (if needed)**:
    ```sh
    export PYTHONPATH=$(pwd)
    ```

2. **Start the Celery worker**:
    ```sh
    celery -A celery_app.celery_app worker --loglevel=info
    ```

### Step 3: Start the FastAPI Application

Ensure your Python environment is activated, then run the following command:

1. **Start FastAPI with Uvicorn**:
    ```sh
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

### Full Command Sequence

Here’s a summarized sequence of commands to start Redis, Celery, and FastAPI:

#### On Ubuntu

```sh
# Install and start Redis
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Navigate to your project directory
cd /path/to/your/project

# Set the Python path
export PYTHONPATH=$(pwd)

# Start the Celery worker
celery -A celery_app.celery_app worker --loglevel=info
```

#### On macOS

```sh
# Install and start Redis
brew install redis
redis-server /usr/local/etc/redis.conf

# Navigate to your project directory
cd /path/to/your/project

# Set the Python path
export PYTHONPATH=$(pwd)

# Start the Celery worker
celery -A celery_app.celery_app worker --loglevel=info
```

Finally, in a separate terminal:

```sh
# Navigate to your project directory
cd /path/to/your/project

# Start FastAPI with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
