from django.urls import path
from . import views

urlpatterns = [  
    path('customer/<int:room_id>/', views.customer_chat, name="customer_chat"),
    path('dashboard/', views.chat_dashboard, name="chat_dashboard"),
    path('superuser/<int:room_id>/', views.superuser_chat, name="superuser_chat"),
    path('customer/complete/<int:room_id>/', views.customer_complete_chat, name="customer_complete_chat"),
    path('superuser/complete/<int:room_id>/', views.superuser_complete_chat, name="superuser_complete_chat"),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('chat-history/', views.chat_history_customer, name='chat_history_customer'),
]