from django.utils import timezone
from django.http import JsonResponse
from dotenv import load_dotenv
from .models import StudentApplication, SyncLog
import os
import requests

load_dotenv()

SALESFORCE_INSTANCE = 'https://orgfarm-953ff40aa4-dev-ed.develop.my.salesforce.com'

def get_salesforce_token():
    url = f"{SALESFORCE_INSTANCE}/services/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('SALESFORCE_CLIENT_ID'),
        'client_secret': os.getenv('SALESFORCE_CLIENT_SECRET'),
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def test_salesforce_connection(request):
    token = get_salesforce_token()
    if token:
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully connected to Salesforce',
            'instance_url': SALESFORCE_INSTANCE,
            'token_preview': token[:20] + '...'
        })
    return JsonResponse({
        'status': 'error',
        'message': 'Failed to connect to Salesforce'
    }, status=500)


def sync_salesforce_contacts(request):
    token = get_salesforce_token()
    if not token:
        return JsonResponse({
            'status': 'error',
            'message': 'Could not connect to Salesforce'
        }, status=500)

    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Query contacts from Salesforce
        query = "SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 10"
        response = requests.get(
            f"{SALESFORCE_INSTANCE}/services/data/v59.0/query/",
            headers=headers,
            params={'q': query}
        )

        if response.status_code != 200:
            return JsonResponse({
                'status': 'error',
                'message': f'Salesforce query failed: {response.json()}'
            }, status=500)

        records = response.json().get('records', [])
        synced = 0

        for record in records:
            salesforce_id = record.get('Id')
            first_name = record.get('FirstName', '') or ''
            last_name = record.get('LastName', '') or ''
            full_name = f"{first_name} {last_name}".strip()
            email = record.get('Email', '') or ''

            if not email:
                continue

            obj, created = StudentApplication.objects.update_or_create(
                salesforce_id=salesforce_id,
                defaults={
                    'student_name': full_name,
                    'student_email': email,
                    'student_id': salesforce_id[:10],
                    'application_status': 'submitted',
                    'course_name': 'Bachelor of Information Technology',
                    'intake_year': 2026,
                    'intake_semester': 'Semester 1',
                    'last_synced': timezone.now(),
                }
            )
            synced += 1

        SyncLog.objects.create(
            sync_status='success',
            records_synced=synced,
            records_failed=0
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Synced {synced} records from Salesforce',
            'records_synced': synced,
            'records': [
                {
                    'id': r.get('Id'),
                    'name': f"{r.get('FirstName','')} {r.get('LastName','')}".strip(),
                    'email': r.get('Email', '')
                } for r in records
            ]
        })

    except Exception as e:
        SyncLog.objects.create(
            sync_status='failed',
            records_synced=0,
            records_failed=1,
            error_message=str(e)
        )
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)