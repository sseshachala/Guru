# API for getting the base code for AI project

This project demonstrates a simple file upload using FastAPI, including logging and test cases.

## Installation

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

