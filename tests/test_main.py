import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Load API key from .env.json file
with open(os.path.join(os.path.dirname(__file__), '..', '.env.json')) as f:
    config = json.load(f)
API_KEY = config["API_KEY"]

def test_upload_files():
    file_content = b"test file content"
    files = [
        ("files", ("test1.txt", file_content, "text/plain")),
        ("files", ("test2.txt", file_content, "text/plain"))
    ]
    response = client.post(
        "/upload-files",
        headers={"access_token": API_KEY},
        files=files
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["filename"] == "test1.txt"
    assert response_data[0]["content_type"] == "text/plain"
    assert response_data[0]["message"] == "File uploaded successfully"
    assert response_data[1]["filename"] == "test2.txt"
    assert response_data[1]["content_type"] == "text/plain"
    assert response_data[1]["message"] == "File uploaded successfully"

def test_upload_files_invalid_key():
    file_content = b"test file content"
    files = [
        ("files", ("test1.txt", file_content, "text/plain")),
        ("files", ("test2.txt", file_content, "text/plain"))
    ]
    response = client.post(
        "/upload-files",
        headers={"access_token": "invalid_key"},
        files=files
    )
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Could not validate credentials"

def test_upload_files_exception_handling(mocker):
    mocker.patch("app.utils.save_file", side_effect=Exception("Test exception"))
    file_content = b"test file content"
    files = [
        ("files", ("test1.txt", file_content, "text/plain")),
        ("files", ("test2.txt", file_content, "text/plain"))
    ]
    response = client.post(
        "/upload-files",
        headers={"access_token": API_KEY},
        files=files
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert "An error occurred while uploading the file: Test exception" in response_data[0]["message"]
    assert "An error occurred while uploading the file: Test exception" in response_data[1]["message"]
