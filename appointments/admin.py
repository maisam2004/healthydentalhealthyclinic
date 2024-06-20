from django.contrib import admin

# Register your models here.
from .models import Dentist,Appointment

admin.site.register(Dentist)
admin.site.register(Appointment)



