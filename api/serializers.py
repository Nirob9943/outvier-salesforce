from rest_framework import serializers
from salesforce_integration.models import StudentApplication, SyncLog
from notifications.models import Notification


class StudentApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = [
            'id',
            'salesforce_id',
            'student_name',
            'student_email',
            'student_id',
            'application_status',
            'course_name',
            'intake_year',
            'intake_semester',
            'offer_details',
            'offer_deadline',
            'documents_verified',
            'missing_documents',
            'last_communication',
            'last_synced',
            'updated_at',
        ]


class StudentApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = [
            'id',
            'student_name',
            'student_id',
            'application_status',
            'course_name',
            'documents_verified',
            'missing_documents',
            'last_synced',
        ]


class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLog
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'