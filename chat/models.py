from django.db import models
from django.utils import timezone

from customer.models import Customer
from superuser.models import Superadmin
from services.models import ServiceBooking 


# .............ChatMessage Model.............
class ChatMessage(models.Model):

    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE, related_name='messages')
    SENDER_CHOICES = (('customer', 'Customer'), ('superuser', 'Superuser'),)
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,
                                 null=True, blank=True, related_name='chat_messages'
                                )
    superuser = models.ForeignKey(Superadmin, on_delete=models.CASCADE,
                                  null=True, blank=True, related_name='chat_messages'
                                )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} - Room {self.room.id}"

    def save(self, *args, **kwargs):
        """
        Validate sender before saving.
        """
        if self.sender == "customer":
            self.superuser = None
            if not self.customer:
                raise ValueError("Customer must be set for customer messages.")

        elif self.sender == "superuser":
            self.customer = None
            if not self.superuser:
                raise ValueError("Superuser must be set for superuser messages.")

        super().save(*args, **kwargs)



# .............ChatRoom Model.............
class ChatRoom(models.Model):

    STATUS_CHOICES = (("Pending", "Pending"), ("Completed", "Completed"),)
    booking = models.OneToOneField(ServiceBooking, on_delete=models.CASCADE, related_name="chat_room")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="chat_rooms")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    customer_completed = models.BooleanField(default=False)
    superuser_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def check_completion(self):
        """
        Automatically mark the chat completed
        when both customer and superuser finish it.
        """
        if self.customer_completed and self.superuser_completed:
            self.status = "Completed"
            self.completed_at = timezone.now()

    def save(self, *args, **kwargs):
        self.check_completion()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Chat #{self.id} - Booking #{self.booking.id}"