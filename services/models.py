from django.db import models
from django.contrib.auth.models import User
from customer.models import Vehicle, City
from mechanic.models import Mechanic
from customer.models import Customer
# Create your models here.

class Complaints(models.Model):
    complaint_name = models.CharField(255)
    basic_sevice_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.complaint_name} - {self.basic_sevice_price}"
    

class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ("Pending", "pending"),
        ("Assigned", "assigned"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("In_progress", "In progress"),
        ("Completed", "Completed"),
        ("Cancelled", "cancelled")
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    complaints = models.ManyToManyField(Complaints)
    problem_description = models.TextField()
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE, blank=True, null=True)
    labour_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        complaint_name = ", ".join(
            complaint.name for complaint in self.complaints
        )
        return f"{self.customer.name} - {complaint_name} - {self.status}"


    