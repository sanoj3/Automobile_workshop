from django.urls import path
from . import views

urlpatterns = [
    path('forgot-password/', views.forgot_password, name="forgot_password"),
    path('verify-otp/', views.verify_otp, name="verify_otp"),
    path('resend-otp/', views.resend_otp, name="resend_otp"),
    path('reset-password/', views.reset_password, name="reset_password"),
    path('mechanic-forgot-password/', views.forgot_password_mechanic, name="forgot_password_mechanic"),
    path('mechanic-verify-otp/', views.verify_otp_mechanic, name="verify_otp_mechanic"),
    path('mechanic-resend-otp/', views.resend_otp_mechanic, name="resend_otp_mechanic"),
    path('mechanic-reset-password/', views.reset_password_mechanic, name="reset_password_mechanic"),
]