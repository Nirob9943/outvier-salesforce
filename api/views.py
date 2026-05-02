from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from salesforce_integration.models import StudentApplication, SyncLog
from notifications.models import Notification
from .serializers import (
    StudentApplicationSerializer,
    StudentApplicationStatusSerializer,
    SyncLogSerializer,
    NotificationSerializer,
)


class StudentApplicationListView(generics.ListAPIView):
    """
    GET /api/applications/
    Returns all student applications.
    Admin users see all records.
    """
    serializer_class = StudentApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return StudentApplication.objects.all().order_by('-updated_at')
        return StudentApplication.objects.filter(
            student_email=user.email
        ).order_by('-updated_at')


class StudentApplicationDetailView(generics.RetrieveAPIView):
    """
    GET /api/applications/<id>/
    Returns one specific student application by ID.
    """
    serializer_class = StudentApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return StudentApplication.objects.all()
        return StudentApplication.objects.filter(student_email=user.email)


class StudentApplicationStatusView(generics.ListAPIView):
    """
    GET /api/applications/status/
    Returns a summary of all student application statuses.
    """
    serializer_class = StudentApplicationStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return StudentApplication.objects.all().order_by('-updated_at')
        return StudentApplication.objects.filter(
            student_email=user.email
        ).order_by('-updated_at')


class SyncLogListView(generics.ListAPIView):
    """
    GET /api/sync-logs/
    Returns all Salesforce sync logs. Admin only.
    """
    serializer_class = SyncLogSerializer
    permission_classes = [IsAdminUser]
    queryset = SyncLog.objects.all().order_by('-synced_at')


class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates a user and returns an auth token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_staff,
            })

        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Logs out the user by deleting their auth token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            {'status': 'success', 'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )


class APIStatusView(APIView):
    """
    GET /api/
    Returns the API status and available endpoints.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'online',
            'project': 'Outvier Salesforce Integration API',
            'version': '1.0',
            'endpoints': {
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'applications': '/api/applications/',
                'application_detail': '/api/applications/<id>/',
                'application_status': '/api/applications/status/',
                'sync_logs': '/api/sync-logs/',
                'salesforce_test': '/salesforce/test-connection/',
                'salesforce_sync': '/salesforce/sync-contacts/',
            }
        })