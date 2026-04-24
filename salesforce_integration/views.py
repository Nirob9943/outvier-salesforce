from django.utils import timezone
from django.http import JsonResponse
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from dotenv import load_dotenv
from .models import StudentApplication, SyncLog
import os

load_dotenv()


def get_salesforce_connection():
    try:
        sf = Salesforce(
            username=os.getenv('SALESFORCE_USERNAME'),
            password=os.getenv('SALESFORCE_PASSWORD'),
            consumer_key=os.getenv('SALESFORCE_CLIENT_ID'),
            consumer_secret=os.getenv('SALESFORCE_CLIENT_SECRET'),
            domain=os.getenv('SALESFORCE_DOMAIN')
        )
        return sf
    except SalesforceAuthenticationFailed as e:
        print(f"Salesforce authentication failed: {e}")
        return None
    except Exception as e:
        print(f"Salesforce connection error: {e}")
        return None


def test_salesforce_connection(request):
    sf = get_salesforce_connection()
    if sf:
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully connected to Salesforce',
            'instance_url': sf.base_url
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to connect to Salesforce'
        }, status=500)


def sync_salesforce_contacts(request):
    sf = get_salesforce_connection()
    if not sf:
        return JsonResponse({
            'status': 'error',
            'message': 'Could not connect to Salesforce'
        }, status=500)

    try:
        # Query contacts from Salesforce
        result = sf.query(
            "SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 10"
        )
        records = result.get('records', [])
        synced = 0

        for record in records:
            salesforce_id = record.get('Id')
            first_name = record.get('FirstName', '') or ''
            last_name = record.get('LastName', '') or ''
            full_name = f"{first_name} {last_name}".strip()
            email = record.get('Email', '') or ''

            if not email:
                continue

            # Create or update student application
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

        # Log the sync
        SyncLog.objects.create(
            sync_status='success',
            records_synced=synced,
            records_failed=0
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Synced {synced} records from Salesforce',
            'records_synced': synced
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