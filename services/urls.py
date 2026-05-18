from django.urls import path
from . import views

urlpatterns = [
    path('servicebooking/', views.servicebooking, name='servicebooking'),
    path('service_booking_success/', views.service_booking_success, name='service_booking_success'),
    
]