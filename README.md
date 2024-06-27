# API for getting the base code for AI project

This project demonstrates a simple file upload using FastAPI, including logging and test cases.

## Installation

# For DO - run system_config.sh and pre-requisites.sh

1. Create and activate a virtual environment (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. Run the FastAPI application:
    ```sh
    uvicorn app.main:app --reload
    ```

## Running Tests

1. Run tests and generate an HTML report:
    ```sh
    pytest --html=report.html --self-contained-html
    ```

## API Key

The API key for accessing the file upload endpoint should be included in the request headers as `access_token`. The key is read from a `.env.json` file.

## Example cURL Command

```sh
curl -X POST "http://localhost:8000/api/upload-files" -H "access_token: test123" -F "files=@path_to_your_file1" -F "files=@path_to_your_file2"
curl -X POST "http://localhost:8000/api/transcript-youtube" \
    -H "access_token: test123" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=5hMgUbmrENM"}'

curl -X POST "http://localhost:8000/upload" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/path/to/your/file.pdf"
curl -X POST "http://localhost:8000/query" -H "accept: application/json" -H "Content-Type: application/json" -d '{
  "embedding": [0.1, 0.2, 0.3, ...],
  "query": "What is the content of the document?"
}'
curl -X GET "http://localhost:8000/view/file.pdf" -H "accept: text/plain"



For dev server on DO - ubuntu

wget the systemconfig.sh from git (Raw version)
chmod +x systemconfig

sudo ./system_config <username> <"SSH Key String">


git clone <repository>

cd <project_name> # Ex cd Guru
chmod +x pre-requistes.sh

cp develop-env.json .env.json
modify DB and OPENAI_API_KEY KEY

run ./pre-requistes.sh requirements.txt
Then provide username, group and working directory  for the linux

# Check Redis status
sudo systemctl status redis-server
redis-cli ping

# Check Celery status
sudo systemctl status celery.service
ps aux | grep 'celery worker'

# Check Gunicorn status
sudo systemctl status app.main
ps aux | grep gunicorn



