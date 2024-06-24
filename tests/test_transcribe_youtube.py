import requests
import json

# Define the API endpoint and API key
url = "http://localhost:8000/api/v1/transcript-youtube"
jwt_token = "test123"  # Replace with your actual API key

# Define the payload
payload = {
    "url": "https://www.youtube.com/watch?v=fCUkvL0mbxI"
}

# Define the headers
headers = {
    "Authorization": f"Bearer {jwt_token}"
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))
# Print the response
print(response.status_code)
print(response.json())
print(response.json().get("task_id"))



