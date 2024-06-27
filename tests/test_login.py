import requests

# Define the base URL of your FastAPI application
BASE_URL = "http://localhost:8000"

# Define the login endpoint
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/login/"

# Define the login data for valid and invalid scenarios
valid_login_data = {
    "email": "newuser@example.com",  # This should be an existing user in your database
    "password": "newpassword"
}

invalid_login_data = {
    "email": "newuser@example.com",  # This should be an existing user in your database
    "password": "wrongpassword"
}

nonexistent_login_data = {
    "email": "nonexistentuser@example.com",  # This should be a non-existent user
    "password": "somepassword"
}

def test_login(login_data, expected_status_code, expected_detail=None):
    # Send a POST request to the login endpoint
    response = requests.post(LOGIN_ENDPOINT, json=login_data)
    
    # Print the status code of the response
    print(f"Status Code: {response.status_code}")
    
    # Print the JSON response or error message
    try:
        response_json = response.json()
        print("Response JSON:")
        print(response_json)
    except requests.exceptions.JSONDecodeError:
        print("Response Text:")
        print(response.text)
        response_json = None

    # Assert the response status code is as expected
    assert response.status_code == expected_status_code, f"Expected status code {expected_status_code}, but got {response.status_code}"
    
    # Assert that the response contains the expected details
    if expected_detail:
        assert response_json is not None and response_json.get('detail') == expected_detail, f"Unexpected error message: {response_json.get('detail')}"
    else:
        assert response_json is not None and "token" in response_json, "Token not found in the response"
    
    print("Test passed")

# Run the tests
if __name__ == "__main__":
    print("Testing with valid credentials...")
    test_login(valid_login_data, 200)
    
    print("\nTesting with invalid password...")
    test_login(invalid_login_data, 400, "Invalid credentials")
    
    print("\nTesting with non-existent user...")
    test_login(nonexistent_login_data, 400, "Invalid credentials")
