from django.contrib import admin
from .models import Complaints, ServiceBooking, MechanicRequest, Bill, BookingSparePart, Feedback
# Register your models here.

admin.site.register(Complaints),
admin.site.register(ServiceBooking),
admin.site.register(MechanicRequest),
admin.site.register(Bill),
admin.site.register(BookingSparePart),
admin.site.register(Feedback),