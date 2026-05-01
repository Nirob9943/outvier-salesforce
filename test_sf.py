from dotenv import load_dotenv
import os
import requests

load_dotenv()

client_id = os.getenv('SALESFORCE_CLIENT_ID')
client_secret = os.getenv('SALESFORCE_CLIENT_SECRET')
username = os.getenv('SALESFORCE_USERNAME')
password = os.getenv('SALESFORCE_PASSWORD')

# All possible domain formats to try
domains = [
    'https://login.salesforce.com',
    'https://test.salesforce.com',
    'https://orgfarm-953ff40aa4-dev-ed.develop.my.salesforce.com',
    'https://orgfarm-953ff40aa4-dev-ed.develop.my.salesforce-setup.com',
]

print("=" * 60)
print("TESTING CLIENT CREDENTIALS FLOW")
print("=" * 60)
for domain in domains:
    url = f"{domain}/services/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"\nDomain: {domain}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("*** SUCCESS! ***")
            data = response.json()
            print(f"Access Token: {data.get('access_token', '')[:30]}...")
            print(f"Instance URL: {data.get('instance_url', '')}")
    except Exception as e:
        print(f"\nDomain: {domain}")
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("TESTING USERNAME PASSWORD FLOW")
print("=" * 60)
for domain in domains:
    url = f"{domain}/services/oauth2/token"
    payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"\nDomain: {domain}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("*** SUCCESS! ***")
            data = response.json()
            print(f"Access Token: {data.get('access_token', '')[:30]}...")
            print(f"Instance URL: {data.get('instance_url', '')}")
    except Exception as e:
        print(f"\nDomain: {domain}")
        print(f"Error: {e}")
