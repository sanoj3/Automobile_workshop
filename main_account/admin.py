from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(PasswordResetOTP)
admin.site.register(MechanicPasswordOTP)
admin.site.register(Fixigo)