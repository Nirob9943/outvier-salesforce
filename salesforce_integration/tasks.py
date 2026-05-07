from celery import shared_task
from django.utils import timezone
from .models import StudentApplication, SyncLog
import os
import requests
from dotenv import load_dotenv

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


@shared_task(bind=True, max_retries=3)
def sync_salesforce_data(self):
    """
    Automatic Celery task that syncs Salesforce Contact data
    into the PostgreSQL database every 15 minutes.
    """
    try:
        token = get_salesforce_token()
        if not token:
            raise Exception('Failed to get Salesforce access token')

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Query contacts from Salesforce
        query = "SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 50"
        response = requests.get(
            f"{SALESFORCE_INSTANCE}/services/data/v59.0/query/",
            headers=headers,
            params={'q': query}
        )

        if response.status_code != 200:
            raise Exception(f'Salesforce query failed: {response.json()}')

        records = response.json().get('records', [])
        synced = 0
        failed = 0
        status_changes = []

        for record in records:
            try:
                salesforce_id = record.get('Id')
                first_name = record.get('FirstName', '') or ''
                last_name = record.get('LastName', '') or ''
                full_name = f"{first_name} {last_name}".strip()
                email = record.get('Email', '') or ''

                if not email:
                    continue

                # Check if record exists and get old status
                existing = StudentApplication.objects.filter(
                    salesforce_id=salesforce_id
                ).first()

                old_status = existing.application_status if existing else None

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

                # Detect status changes for notifications
                if old_status and old_status != obj.application_status:
                    status_changes.append({
                        'student_name': full_name,
                        'email': email,
                        'old_status': old_status,
                        'new_status': obj.application_status
                    })

                synced += 1

            except Exception as e:
                failed += 1
                print(f"Error syncing record {record.get('Id')}: {e}")

        # Log the sync result
        sync_status = 'success' if failed == 0 else 'partial' if synced > 0 else 'failed'
        SyncLog.objects.create(
            sync_status=sync_status,
            records_synced=synced,
            records_failed=failed
        )

        # Trigger notifications for status changes
        if status_changes:
            for change in status_changes:
                send_status_change_notification.delay(
                    change['student_name'],
                    change['email'],
                    change['old_status'],
                    change['new_status']
                )

        return {
            'status': sync_status,
            'records_synced': synced,
            'records_failed': failed,
            'status_changes': len(status_changes)
        }

    except Exception as exc:
        # Retry up to 3 times with exponential backoff
        SyncLog.objects.create(
            sync_status='failed',
            records_synced=0,
            records_failed=1,
            error_message=str(exc)
        )
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task
def send_status_change_notification(student_name, email, old_status, new_status):
    """
    Sends an email notification to a student when their
    application status changes in Salesforce.
    """
    from django.core.mail import send_mail
    from notifications.models import Notification
    from salesforce_integration.models import StudentApplication

    try:
        application = StudentApplication.objects.filter(
            student_email=email
        ).first()

        message = f"""
Dear {student_name},

Your application status has been updated.

Previous Status: {old_status.replace('_', ' ').title()}
New Status: {new_status.replace('_', ' ').title()}

Please log in to the Outvier app to view more details about your application.

Best regards,
Outvier Admissions Team
        """

        send_mail(
            subject=f'Application Status Update — {new_status.replace("_", " ").title()}',
            message=message,
            from_email='noreply@outvier.edu.au',
            recipient_list=[email],
            fail_silently=True,
        )

        # Record notification in database
        if application:
            Notification.objects.create(
                application=application,
                notification_type='status_change',
                title=f'Status Updated: {new_status.replace("_", " ").title()}',
                message=message,
                is_sent=True,
                sent_at=timezone.now()
            )

    except Exception as e:
        print(f"Failed to send notification to {email}: {e}")