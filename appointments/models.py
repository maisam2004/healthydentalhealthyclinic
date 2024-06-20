from django.db import models
from django.contrib.auth.models import User
import uuid
from fee.models import Fee




class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f'{self.name}'



class Dentist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dentist')
    services = models.ManyToManyField(Fee, related_name='dentists', blank=True) 

    def __str__(self):
        return self.user.get_full_name()





class Appointment(models.Model):
    full_name = models.CharField(max_length=100,null=True)
    email = models.EmailField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    phone_number = models.CharField(max_length=20,null=True) 
    dentist = models.ForeignKey(Dentist, on_delete=models.CASCADE, blank=True, null=True, related_name='appointments')
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    
    service = models.ForeignKey(Fee, on_delete=models.CASCADE, null=True)
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True)
    reference_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Appointment - {self.reference_number}"