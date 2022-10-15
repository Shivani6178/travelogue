from django.contrib import admin
from .models import CustomerProfile, Bookings

# Register your models here.
admin.site.register(CustomerProfile)
admin.site.register(Bookings)
