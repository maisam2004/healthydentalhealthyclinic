from django.contrib import messages
from django.contrib.messages import get_messages
from django.views.generic import TemplateView
from appointments.models import Dentist 

# Create your views here.
from django.shortcuts import render, redirect
from .forms import ContactForm
from .models import Contact

def contact(request):
    """
    Handles the rendering and submission of the contact form.

    This view function:
    1. Renders the contact form template.
    2. Processes form submission, validating data and associating it with a user (if logged in).
    3. Saves the contact message to the database on successful validation.
    4. Displays success or error messages to the user.
    5. Renders the contact form again, either with a blank form or with the submitted data and error messages.

    Args:
        request: The HttpRequest object representing the current request.

    Returns:
        HttpResponse: An HTTP response containing the rendered contact form template with context data.
    """

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.user = request.user
            contact.save()
            print(contact)
            messages.success(request, 'Your message has been sent successfully!')
            form = ContactForm()  # Reset the form after successful submission
        else:
            # Log form errors
            print(form.errors)
            messages.error(request, 'There was an error submitting your message.')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'messages': messages.get_messages(request),
    }
    return render(request, 'contact/contact.html', context)

class AboutTemplateView(TemplateView):
    " to show about us page and showing dentists staff "
    template_name = "contact/about.html"
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['dentists'] = Dentist.objects.all()  # Fetch all dentists
            return context

    
