from django.db import models
from django.utils import timezone

from datetime import timedelta

from customer.models import Vehicle, City
from mechanic.models import Mechanic, StockManagement
from customer.models import Customer



#::::::::::::::::::::::Complaints Model::::::::::::::::::::::
class Complaints(models.Model):
    complaint_name = models.CharField(255)
    basic_service_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.complaint_name} - {self.basic_service_price}"
    

#::::::::::::::::::::::Service Booking Model::::::::::::::::::::::
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
    location = models.TextField()
    problem_description = models.TextField()
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.SET_NULL, blank=True, null=True)
    labour_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rejected_mechanics = models.ManyToManyField(Mechanic, blank=True, related_name="rejected_bookings")
    cancel_reason = models.TextField(blank=True, null=True)
    cancelled_by = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        complaints = ", ".join([c.complaint_name for c in self.complaints.all()])
        return f"{self.customer.name} - {complaints} - {self.status}"


#::::::::::::::::::::::Mechanic Request::::::::::::::::::::::
class MechanicRequest(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('In_progress', 'In_progress'),
        ("Completed", "Completed"),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    ]

    booking = models.ForeignKey(ServiceBooking, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):

        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)

        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.booking.id} - {self.mechanic.name} - {self.status}"
    

#::::::::::::::::::::::Bill Model::::::::::::::::::::::
class Bill(models.Model):

    booking = models.OneToOneField(ServiceBooking, on_delete=models.CASCADE)
    complaint_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spare_parts_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_parts_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labour_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=50,choices=[
                                    ('Pending', 'Pending'),
                                    ('Paid', 'Paid')
                                    ],default='Pending')
    payment_id = models.CharField(
    max_length=200,
    null=True,
    blank=True
)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.booking.customer.name}"
    

#::::::::::::::::::::::Booking Spareparts Model::::::::::::::::::::::
class BookingSparePart(models.Model):

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockManagement, on_delete=models.SET_NULL, null=True, blank=True)
    part_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_extra = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.part_name
    

#::::::::::::::::::::::Customer Rating Model::::::::::::::::::::::
class Feedback(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name='feedback')
    service = models.OneToOneField('services.ServiceBooking', on_delete=models.CASCADE)
    mechanic = models.ForeignKey('mechanic.Mechanic', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.id} - {self.customer} - {self.rating} - {self.mechanic}"
    

