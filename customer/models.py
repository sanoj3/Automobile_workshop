from django.db import models
from django.contrib.auth.models import User


# .............City Database.............
class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# .............Customer Database.............
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=15)
    address = models.TextField()
    profile_pic = models.ImageField(upload_to='profile_pic/',null=True, blank=True)
    city = models.ForeignKey('customer.City', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
 # .............Customer Vehicle Database.............  
class Vehicle(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name="vehicles")
    vehicle_name = models.CharField(max_length=255)
    vehicle_model = models.CharField(max_length=200)
    vehicle_year = models.IntegerField()
    vehicle_number = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.customer.name} - {self.vehicle_number}"
    


    
