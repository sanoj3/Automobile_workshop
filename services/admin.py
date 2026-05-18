from django.contrib import admin
from .models import Complaints, ServiceBooking
# Register your models here.

admin.site.register(Complaints),
admin.site.register(ServiceBooking),