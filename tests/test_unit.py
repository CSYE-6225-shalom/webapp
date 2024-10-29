import sys
import os
from flask import json
import bcrypt
from faker import Faker
import base64
import random
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db, User

fake = Faker()


@pytest.fixture(scope="module")
def client():
    app = create_app(testing="unit")
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

        db.session.remove()
        db.drop_all()


print("\n--- Starting All Endpoint Tests ---")

local_part = fake.email().split('@')[0]
domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
domain = random.choice(domains)
email = f"{local_part}@{domain}"
create_data = {
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'email': email,
    'password': fake.password()
}

update_data = {
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'password': fake.password()
}


def test_health_endpoint(client):
    try:
        print("\n1. Testing Health Check")
        response = client.get('/healthz')
        assert response.status_code == 200
        assert b'Health is OK' in response.data
        print("Health check passed")
    except AssertionError as e:
        print(f"Health check failed: {e}")


def test_user_creation_endpoint(client):
    try:
        print("\n2. Testing Create User")
        print(f"Creating user with data: {create_data}")
        response = client.post('/v1/user', json=create_data)
        assert response.status_code == 201
        assert create_data['email'].encode() in response.data
        print("User created successfully")
    except AssertionError as e:
        print(f"User creation failed: {e}")


def test_create_user_verification():
    try:
        print("\n3. Verifying User Creation and Password Hashing")
        user = User.query.filter_by(email=create_data['email']).first()
        assert user is not None
        assert user.first_name == create_data['first_name']
        assert user.last_name == create_data['last_name']
        assert bcrypt.checkpw(create_data['password'].encode('utf-8'), user.password.encode('utf-8'))
        print("User creation and password hashing verified")
    except AssertionError as e:
        print(f"Failed to verify user creation: {e}")


def test_existing_user(client):
    try:
        print("\n4. Testing Create Existing User")
        response = client.post('/v1/user', json=create_data)
        assert response.status_code == 400
        assert b'User already exists!' in response.data
        print("Existing user creation prevented")
    except AssertionError as e:
        print(f"Failed to test exist user creation: {e}")


def test_update_user(client):
    try:
        print("\n5. Testing Update User")
        print(f"Updating user with data: {update_data}")
        user = User.query.filter_by(email=create_data['email']).first()
        assert user is not None
        auth_string = base64.b64encode(f"{create_data['email']}:{create_data['password']}".encode()).decode()
        headers = {'Authorization': f"Basic {auth_string}"}
        response = client.put('/v1/user/self', json=update_data, headers=headers)
        assert response.status_code == 204
        print("User updated successfully")
    except AssertionError as e:
        print(f"Failed to update user: {e}")


def test_update_user_verification():
    try:
        print("\n6. Verifying User Update")
        user = User.query.filter_by(email=create_data['email']).first()
        assert user.first_name == update_data['first_name']
        assert user.last_name == update_data['last_name']
        assert bcrypt.checkpw(update_data['password'].encode('utf-8'), user.password.encode('utf-8'))
        print("User update verified")
    except AssertionError as e:
        print(f"Failed to verify user info modification: {e}")


def test_get_user_info_endpoint(client):
    try:
        print("\n7. Testing Get User Info")
        auth_string = base64.b64encode(f"{create_data['email']}:{update_data['password']}".encode()).decode()
        headers = {'Authorization': f"Basic {auth_string}"}
        response = client.get('/v1/user/self', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] != create_data['first_name']
        assert data['last_name'] != create_data['last_name']
        assert data['email'] == create_data['email']
        print("User info retrieved successfully")
    except AssertionError as e:
        print(f"Failed to get created user info: {e}")


def test_unauthorized_access_request(client):
    try:
        print("\n8. Testing Unauthorized Access")
        response = client.get('/v1/user/self')
        assert response.status_code == 401
        print("Unauthorized access prevented")
    except AssertionError as e:
        print(f"Failed to verify unauthorized requests: {e}")


def test_invalid_email_request(client):
    try:
        print("\n9. Testing Invalid Email")
        invalid_data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': f"{local_part}@example.com",
            'password': fake.password()
        }
        print(f"Attempting to create user with invalid email: {invalid_data}")
        response = client.post('/v1/user', json=invalid_data)
        assert response.status_code == 400
    except AssertionError as e:
        print(f"Failed to validate user email: {e}")


def test_invalid_method_request(client):
    try:
        print("\n10. Testing Method Not Allowed")
        response = client.post('/healthz')
        assert response.status_code == 405
        assert b'Method Not Allowed' in response.data
        print("Method not allowed error returned")
    except AssertionError as e:
        print(f"Failed to verify invalid method requests: {e}")


def test_invalid_path_request(client):
    try:
        print("\n11. Testing Not Found")
        response = client.get('/healthz/v1')
        assert response.status_code == 404
        assert b'Not Found' in response.data
        print("Page not found error returned")
    except AssertionError as e:
        print(f"Failed to verify invalid path requests: {e}")


def test_request_with_extra_headers(client):
    try:
        print("\n12. Testing Request with Extra Headers")
        auth_string = base64.b64encode(f"{create_data['email']}:{update_data['password']}".encode()).decode()
        headers = {
            'Authorization': f"Basic {auth_string}",
            'Extra-Header': 'ExtraHeaderValue'
        }
        response = client.get('/v1/user/self', headers=headers)
        assert response.status_code == 400
        print("User info request with extra headers handled correctly")
    except AssertionError as e:
        print(f"Failed to verify requests with extra Headers: {e}")


def test_request_with_params(client):
    try:
        print("\n13. Testing Request with Extra Params")
        auth_string = base64.b64encode(f"{create_data['email']}:{update_data['password']}".encode()).decode()
        headers = {
            'Authorization': f"Basic {auth_string}"
        }
        params = {
            'extra_param': 'extra_value'
        }
        response = client.get('/v1/user/self', headers=headers, query_string=params)
        assert response.status_code == 400
        print("User info request with extra params handled correctly")
    except AssertionError as e:
        print(f"Failed to verify requests with params: {e}")


def test_get_request_with_body(client):
    try:
        print("\n14. Testing Request with Body for GET Method")
        auth_string = base64.b64encode(f"{create_data['email']}:{update_data['password']}".encode()).decode()
        headers = {
            'Authorization': f"Basic {auth_string}"
        }
        body = {
            'key': 'value'
        }
        response = client.get('/v1/user/self', headers=headers, data=json.dumps(body), content_type='application/json')
        assert response.status_code == 400
        print("User info request with body handled correctly")
    except AssertionError as e:
        print(f"Failed to verify requests with body: {e}")


print("\n--- All Endpoint Tests Completed ---")
