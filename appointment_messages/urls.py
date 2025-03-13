# appointment_messages/urls.py
from django.urls import path
from . import views

app_name = 'appointment_messages'
urlpatterns = [
    path('send/<int:appointment_id>/', views.send_message, name='send_message'),
    path('conversation/<int:appointment_id>/', views.conversation, name='conversation'),
    path('mark_read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
]