from django.shortcuts import render
from fee.models import Fee, Category
from appointments.models import Service 
# Create your views here.

def fees_list(request):
    """Show list of fees and services from models"""
    fees = Fee.objects.all()
    categories = Category.objects.all()
    context = {
        'fees': fees,
        'categories': categories,
    }
    return render(request, 'fee/fees_list.html', context)




""" fees = [
    Fee(service="Tooth Filling", category=restoractive_category, description="Composite filling", amount=145.00),
    Fee(service="Crowns", category=restoractive_category, description="tooth-shaped cap", amount=360.00),
    Fee(service="Implant", category=restoractive_category, description="permanent solution for missing teeth", amount=400.00),
    Fee(service="Bridges", category=restoractive_category, description="permanent appliance used to replace one or more", amount=800.00),
    Fee(service="Root Canal", category=restoractive_category, description="Root canal treatment", amount=600.00),
    
    # Add more fees as needed
]
Fee.objects.bulk_create(fees)
 """
