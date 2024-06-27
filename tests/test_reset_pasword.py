import requests

# Define the base URL of your FastAPI application
BASE_URL = "http://localhost:8000"

# Define the reset password endpoint
RESET_PASSWORD_ENDPOINT = f"{BASE_URL}/api/v1/reset-password/"

# Define the reset password data for valid and invalid scenarios
valid_reset_password_data = {
    "email": "newuser@example.com",  # This should be an existing user in your database
    "new_password": "newpassword123"
}

invalid_reset_password_data = {
    "email": "nonexistentuser@example.com",  # This should be a non-existent user
    "new_password": "newpassword123"
}

def test_reset_password(reset_data, expected_status_code, expected_detail=None):
    # Send a POST request to the reset password endpoint
    response = requests.post(RESET_PASSWORD_ENDPOINT, json=reset_data)
    
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
        assert response_json is not None and "message" in response_json, "Message not found in the response"
    
    print("Test passed")

# Run the tests
if __name__ == "__main__":
    print("Testing with valid email and new password...")
    test_reset_password(valid_reset_password_data, 200)
    
    print("\nTesting with invalid email and new password...")
    test_reset_password(invalid_reset_password_data, 400, "Invalid email")
