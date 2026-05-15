from django.db import models
from customer.models import City
from django.utils import timezone
# Create your models here.

class Mechanic(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=15)
    address = models.TextField()
    certificate = models.FileField(upload_to='mechanic_certificate/')
    experience_certificate = models.FileField(upload_to='mechanic_experience_certificate/', blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='mechanic_profile_pic/', blank=True, null=True)
    is_valid = models.BooleanField(default=False)
    is_reject = models.BooleanField(default=False)
    last_login_date = models.DateTimeField(blank=True, null=True)
    application_created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if self.is_valid and not self.created_at:
            self.created_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.email}"
    

class Active_mechanic(models.Model):
    mechanic = models.OneToOneField(Mechanic, on_delete=models.CASCADE)
    is_online = models.BooleanField()
    is_available = models.BooleanField()
    is_work_approve = models.BooleanField(blank=True, null=True)
    is_work_reject = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.mechanic.name} - {self.is_online} - {self.is_available}"
    
    

class StockManagement(models.Model):
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    stock_pic = models.ImageField(upload_to='stock_pic/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mechanic.name} - {self.item_name} - {self.quantity} - {self.price}"
    


