from django.contrib import admin
from .models import Complaints, ServiceBooking, MechanicRequest
# Register your models here.

admin.site.register(Complaints),
admin.site.register(ServiceBooking),
admin.site.register(MechanicRequest),