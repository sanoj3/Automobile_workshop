from django.contrib import admin
from .models import Mechanic, Active_mechanic, StockManagement
# Register your models here.

admin.site.register(Mechanic)
admin.site.register(Active_mechanic)
admin.site.register(StockManagement)