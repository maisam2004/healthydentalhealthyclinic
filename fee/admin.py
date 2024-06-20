from django.contrib import admin

# Register your models here.

from .models import Fee, Category

admin.site.register(Fee)
admin.site.register(Category)