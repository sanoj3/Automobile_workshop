from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.


class Superadmin(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)


    def __str__(self):
        return self.username
    
