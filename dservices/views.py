from django.shortcuts import render
from django.shortcuts import render,get_object_or_404,redirect,reverse
from django.contrib import messages
from django.views.generic.base import TemplateView
from fee.models import Fee, Category
# Create your views here.

class GeneralView(TemplateView):
    template_name = 'dservices/general.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the "General" category
        general_category = Category.objects.get(name="General")

        # Get the fees associated with the "General" category
        general_fees = Fee.objects.filter(category=general_category)

        # Add the fees to the context
        context['general_fees'] = general_fees

        return context


""" class CosmeticView(TemplateView):
    template_name = 'dservices/cosmetic.html'


class RestoractiveView(TemplateView):
    template_name = 'dservices/restoractive.html' """

class CosmeticView(TemplateView):
    template_name = 'dservices/cosmetic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cosmetic_category = Category.objects.get(name="Cosmetic")
        cosmetic_fees = Fee.objects.filter(category=cosmetic_category)
        context['cosmetic_fees'] = cosmetic_fees

        return context

class RestoractiveView(TemplateView):
    template_name = 'dservices/restoractive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        restorative_category = Category.objects.get(name="Restorative")
        restorative_fees = Fee.objects.filter(category=restorative_category)
        context['restorative_fees'] = restorative_fees

        return context