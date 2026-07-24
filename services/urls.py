from django.urls import path
from . import views

urlpatterns = [
    path('service-booking/', views.service_booking, name='service_booking'),
    path('booking_success/<int:id>/', views.booking_success, name='booking_success'),
    path('mechanic-requests/', views.mechanic_requests, name='mechanic_requests'),
    path('accept-booking/<int:request_id>/', views.accept_booking, name='accept_booking'),
    path('reject-booking/<int:request_id>/', views.reject_booking, name='reject_booking'),
    path('edit-booking/<int:id>/', views.edit_booking, name='edit_booking'),
    path('booking/cancel/<int:id>/', views.cancel_booking_user, name='cancel_booking_user'),
    path('mechanic/job/cancel/<int:id>/', views.cancel_booking_mechanic, name='cancel_booking_mechanic'),
    path('cancel-booking/<int:id>/', views.cancel_booking_user, name='cancel_booking_user'),
    path('payment/<int:id>/', views.payment_page, name='payment_page'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('feedback/<int:order_id>/', views.feedback, name='feedback'),
]


