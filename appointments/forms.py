from django import forms
from .models import Appointment,Dentist
from fee.models import Fee
from bootstrap_datepicker_plus.widgets import DateTimePickerInput,DatePickerInput,TimePickerInput
from datetime import date,datetime
from datetime import date, timedelta  
import re

import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE


def is_valid_full_name(full_name):
    # Pattern for full names
    # Allows letters (including accents and diacritical marks), spaces, hyphens, and apostrophes
    pattern = r'^[\w\s\-\']+$'
    return bool(re.match(pattern, full_name))


class AppointmentForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Fee.objects.all())
    

    class Meta:
        model = Appointment
        fields = ['full_name', 'phone_number', 'email', 'date','time', 'service', 'notes']

    
        
        widgets = {
            
            'date': DatePickerInput(options={
                    "format": "DD-MM-yyy",  # Format for day, month, and year
                    "minDate": date.today() + timedelta(days=1),  # Key change
                    "daysOfWeekDisabled": [0, 6], 
                    }),

            'time': TimePickerInput(options={
                    "format": "HH:mm",  # Format for day, month, and year
                    "stepping": 30,
                    "enabledHours": [ 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                    
                }),}
    



    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not is_valid_full_name(full_name):
            raise forms.ValidationError('Please enter a valid full name. Allowed characters are letters, spaces, hyphens, and apostrophes.')
        return full_name

    def clean_phone_number(self):
        print("Clean phone number method called")
        phone_number = self.cleaned_data['phone_number']

        try:
            # Changing "GB" to "US" for US phone number validation
            parsed_number = phonenumbers.parse(phone_number, "US")  
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError('Please enter a valid US phone number.')

            # Format the number in E.164 format for consistency (e.g., +12125551212)
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            return formatted_number
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError('Please enter a valid US phone number.')

        

    # You can also define custom fields or widgets here for specific fields
    # Example:
    # date = forms.DateField(widget=forms.SelectDateWidget)
#

""" class AppointmentForm(forms.ModelForm):
    

    class Meta:
        model = Appointment
        fields = ['full_name', 'phone_number', 'email', 'date', 'time', 'service', 'notes']

    
        
        widgets = {
            
            'date': DatePickerInput(options={
                    "format": "DD-MM-yyy",  # Format for day, month, and year
                    "minDate": date.today() + timedelta(days=1),  # Key change
                    "daysOfWeekDisabled": [0, 6], 
                    }),

            'time': TimePickerInput(options={
                    "format": "HH:mm",  # Format for day, month, and year
                    "stepping": 15,
                    "enabledHours": [ 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                    
                }),}
    
   

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not is_valid_full_name(full_name):
            raise forms.ValidationError('Please enter a valid full name. Allowed characters are letters, spaces, hyphens, and apostrophes.')
        return full_name

    def clean_phone_number(self):
        print("Clean phone number method called")
        phone_number = self.cleaned_data['phone_number']
        
        try:
            parsed_number = phonenumbers.parse(phone_number, "GB")  # "GB" is the country code for the UK
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError('Please enter a valid UK phone number')
            
            # Optionally, you can format the phone number for consistency
            formatted_number = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            return formatted_number
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError('Please enter a valid UK phone number')
         """