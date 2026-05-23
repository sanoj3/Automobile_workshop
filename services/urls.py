from django.urls import path
from . import views

urlpatterns = [
    path('service-booking/', views.service_booking, name='service_booking'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('mechanic-requests/', views.mechanic_requests, name='mechanic_requests'),
    path('accept-booking/<int:request_id>/', views.accept_booking, name='accept_booking'),
    path('reject-booking/<int:request_id>/', views.reject_booking, name='reject_booking'),
    path('edit-booking/<int:id>/', views.edit_booking, name='edit_booking'),
       
]


