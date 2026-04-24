from django.urls import path
from . import views

urlpatterns = [
    path('test-connection/', views.test_salesforce_connection, name='test_connection'),
    path('sync-contacts/', views.sync_salesforce_contacts, name='sync_contacts'),
]