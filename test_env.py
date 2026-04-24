from dotenv import load_dotenv
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
import os
import requests

load_dotenv()

# Try direct token request first to see exact error
url = 'https://orgfarm-953ff40aa4-dev-ed.develop.my.salesforce.com/services/oauth2/token'

payload = {
    'grant_type': 'password',
    'client_id': os.getenv('SALESFORCE_CLIENT_ID'),
    'client_secret': os.getenv('SALESFORCE_CLIENT_SECRET'),
    'username': os.getenv('SALESFORCE_USERNAME'),
    'password': os.getenv('SALESFORCE_PASSWORD'),
}

response = requests.post(url, data=payload)
print('Status code:', response.status_code)
print('Response:', response.json())