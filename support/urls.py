from django.urls import path
from . import views
app_name = 'support'

urlpatterns = [
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.view_tickets, name='view_tickets'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
]