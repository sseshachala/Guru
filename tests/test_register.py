import requests

# Define the base URL of your FastAPI application
BASE_URL = "http://159.89.228.58:8000"

# Define the register endpoint
REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/register"

# Define the registration data
register_data = {
    "email": "newuser@example.com",
    "password": "newpassword",
    "keep_logged_in": False
}

def test_register():
    # Send a POST request to the register endpoint
    response = requests.post(REGISTER_ENDPOINT, json=register_data)
    
    # Print the status code of the response
    print(f"Status Code: {response.status_code}")
    
    # Print the JSON response
    print("Response JSON:")
    print(response.json())
    response_json = None
    if response.status_code == 200:
        # Assert that the response contains user details
        assert "user" in response_json, "User details not found in the response"
    elif response.status_code == 400:
        # Assert that the response contains the expected error message
        assert response_json is not None and response_json.get('detail') == 'Email already registered', "Unexpected error message"
    else:
        assert False, f"Unexpected status code {response.status_code}"

# Run the test
if __name__ == "__main__":
    test_register()
