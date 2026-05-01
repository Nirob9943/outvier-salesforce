from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Method 1 - Client Credentials Flow
def try_client_credentials():
    url = f"https://login.salesforce.com/services/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('SALESFORCE_CLIENT_ID'),
        'client_secret': os.getenv('SALESFORCE_CLIENT_SECRET'),
    }
    response = requests.post(url, data=payload)
    print('Method 1 - Client Credentials:')
    print('Status:', response.status_code)
    print('Response:', response.json())
    print()
    return response.json()

# Method 2 - Username Password Flow with instance URL
def try_username_password():
    instance = 'orgfarm-953ff40aa4-dev-ed.develop.my'
    url = f"https://{instance}.salesforce.com/services/oauth2/token"
    payload = {
        'grant_type': 'password',
        'client_id': os.getenv('SALESFORCE_CLIENT_ID'),
        'client_secret': os.getenv('SALESFORCE_CLIENT_SECRET'),
        'username': os.getenv('SALESFORCE_USERNAME'),
        'password': os.getenv('SALESFORCE_PASSWORD'),
    }
    response = requests.post(url, data=payload)
    print('Method 2 - Username Password (instance URL):')
    print('Status:', response.status_code)
    print('Response:', response.json())
    print()
    return response.json()

# Method 3 - Username Password Flow with login URL
def try_login_url():
    url = "https://login.salesforce.com/services/oauth2/token"
    payload = {
        'grant_type': 'password',
        'client_id': os.getenv('SALESFORCE_CLIENT_ID'),
        'client_secret': os.getenv('SALESFORCE_CLIENT_SECRET'),
        'username': os.getenv('SALESFORCE_USERNAME'),
        'password': os.getenv('SALESFORCE_PASSWORD'),
    }
    response = requests.post(url, data=payload)
    print('Method 3 - Username Password (login.salesforce.com):')
    print('Status:', response.status_code)
    print('Response:', response.json())
    print()
    return response.json()

try_client_credentials()
try_username_password()
try_login_url()