from django.db import models
from django.contrib.auth.hashers import make_password
from customer.models import City
# Create your models here.


class Superadmin(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='superuser_profile_pic/', blank=True, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)


    def __str__(self):
        return self.username
    
