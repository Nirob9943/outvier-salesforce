from django.urls import path
from . import views

urlpatterns = [
    path('', views.APIStatusView.as_view(), name='api_status'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('applications/', views.StudentApplicationListView.as_view(), name='application_list'),
    path('applications/status/', views.StudentApplicationStatusView.as_view(), name='application_status'),
    path('applications/<int:pk>/', views.StudentApplicationDetailView.as_view(), name='application_detail'),
    path('sync-logs/', views.SyncLogListView.as_view(), name='sync_logs'),
]