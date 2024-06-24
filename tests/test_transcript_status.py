import requests
import json


url = "http://localhost:8000/api/v1/transcript-task-status/" + "ca6ca794-6311-453f-805e-7a12df4e82da" 
jwt_token = "test123"  # Replace with your actual API key

# Define the payload
payload = {
    "task_id": "90cbab90-7552-48c9-8359-e809293e3593" 
}
# Define the headers
headers = {
    "Authorization": f"Bearer {jwt_token}"
}   

# Send the POST request
response = requests.get(url, headers=headers)
# Print the response
print(response.status_code)
print(response.json())
