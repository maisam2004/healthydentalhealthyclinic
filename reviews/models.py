from django.db import models
from django.contrib.auth.models import User
from appointments.models import Appointment
from pay.models import Order
# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)  # Nullable
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)            # Nullable
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 star rating
    comment = models.TextField()
    image = models.ImageField(upload_to='review_images/', null=True, blank=True)  # Optional image
    created_at = models.DateTimeField(auto_now_add=True)
    def str(self):
        return f"Review by {self.user} on {self.appointment or self. Order}"