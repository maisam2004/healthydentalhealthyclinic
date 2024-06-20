from .models import Review
from django.core.exceptions import ValidationError
from appointments.models import Appointment
from pay.models import Order
from django import forms


class ReviewForm(forms.ModelForm):
    appointment = forms.ModelChoiceField(queryset=Appointment.objects.none(), required=False)
    order = forms.ModelChoiceField(queryset=Order.objects.none(), required=False)

    class Meta:
        model = Review
        fields = ['rating', 'appointment', 'order', 'image', 'comment']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['appointment'].queryset = Appointment.objects.filter(user=user)
        self.fields['order'].queryset = Order.objects.filter(user_profile__user=user)
        self.fields['appointment'].label_from_instance = lambda obj: obj.date.strftime('%Y-%m-%d') if obj.date else str(obj.reference_number)
        
   
    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            # Check file type
            if not image.name.lower().endswith(('.jpg', '.jpeg')):
                raise forms.ValidationError("Only JPG and JPEG images are allowed.")

            # Check file size (e.g., 5 MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size should be less than 5 MB.")

        return image
