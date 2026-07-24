from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import timedelta

from mechanic.models import Mechanic



class Fixigo(models.Model):
    email_customer = models.EmailField()
    email_mechanic = models.EmailField()
    number_customer = models.CharField(max_length=15)
    number_mechanic = models.CharField(max_length=15)
    location = models.CharField()
    address = models.TextField()

    def __str__(self):
        return self.location

# .............Customer Password Reset OTP Database.............
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    

# .............Mechanic Password Reset OTP Database.............
class MechanicPasswordOTP(models.Model):
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)