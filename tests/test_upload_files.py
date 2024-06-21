import requests

# Define the API endpoint and JWT token
url = "http://localhost:8000/api/upload-files"
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTYzMjQ0NTYwMH0.abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567"  # Replace with your actual token

# Define the files to be uploaded
files = {
    'files': ('requirements.txt', open('requirements.txt', 'rb'), 'text/plain'),
    'files': ('dev.txt', open('dev.txt', 'rb'), 'text/plain')
}

# Define the headers
headers = {
    "Authorization": f"Bearer {jwt_token}"
}

# Send the POST request
response = requests.post(url, headers=headers, files=files)

# Print the response
print(response.status_code)
print(response.json())
