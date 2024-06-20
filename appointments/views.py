from django.shortcuts import render, redirect,get_object_or_404
from .models import Service,Appointment,Dentist
from .utils import generate_appointment_qr_code
from .forms import AppointmentForm
from fee.models import Fee  
import random
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import  CreateView, UpdateView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages 
from django.db import transaction  
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required,user_passes_test

#check for as admin -------------
# Check if the user is an admin
def is_admin(user):
    if not user.is_authenticated or not user.is_superuser:
        raise PermissionDenied("You do not have permission to perform this action.")
    else:
        return True

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to perform this action.")

@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def list_appointments(request):
    appointments = Appointment.objects.all().order_by('date', 'time')
    return render(request, 'appointments/admin_list.html', {'appointments': appointments})

login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def cancel_appointment(request, appointment_id):
   
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Cancelled'
    appointment.save()
    try:
        customer_email = appointment.email
        subject = render_to_string(
            'appointments/confirmation_emails/confirmation_email_cancellation_subject.txt',
            {'appointment': appointment}
        )
        body = render_to_string(
            'appointments/confirmation_emails/confirmation_email_cancellation_body.txt',
            {'appointment': appointment, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [customer_email])
        messages.success(request, f'Appointment has been cancelled and a cancellation email has been sent to {appointment.email}.')
    except Exception as e:
        messages.error(request, f'There was an error sending the cancellation email: {e}')

    return redirect('admin_list_appointments')



# Create Appointment
class AppointmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('admin_list_appointments')
    def form_valid(self, form):
        response = super().form_valid(form)  # Save the appointment
        messages.success(self.request, 'Appointment created successfully!')

        # Send notification email to the user (if email exists)
        if self.object.email:  # self.object is the saved Appointment instance
            try:
                customer_email = self.object.email
                subject = render_to_string(
                    'appointments/confirmation_emails/admin_create_appointment_subject.txt', 
                    {'appointment': self.object}
                )
                body = render_to_string(
                    'appointments/confirmation_emails/admin_create_appointment_body.txt',
                    {'appointment': self.object, 'contact_email': settings.DEFAULT_FROM_EMAIL}
                )
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [customer_email])
            except Exception as e:
                # Handle email sending errors (e.g., log them)
                pass 
        
        return response

# Update Appointment
class AppointmentUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('admin_list_appointments')

    def form_valid(self, form):
        response = super().form_valid(form)  # Save the appointment
        messages.success(self.request, 'Appointment updated successfully!')

        # Send notification email 
        if self.object.email:  # self.object is the saved Appointment instance
            try:
                customer_email = self.object.email
                subject = render_to_string(
                    'appointments/confirmation_emails/admin_update_appointment_subject.txt', 
                    {'appointment': self.object}
                )
                body = render_to_string(
                    'appointments/confirmation_emails/admin_update_appointment_body.txt',
                    {'appointment': self.object, 'contact_email': settings.DEFAULT_FROM_EMAIL}
                )
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [customer_email])
            except Exception as e:
                # Handle errors 
                pass 
        
        return response




#=====================================

@login_required(login_url='/accounts/login/')
def success(request, appointment_id):
    """
    Handle successful appointments
    """
    appointment = Appointment.objects.get(id=appointment_id)
    qr_code_data = generate_appointment_qr_code(appointment)
    # Send Confirmation Email
    try:
        customer_email = appointment.email
        subject = render_to_string(
            'appointments/confirmation_emails/confirmation_email_subject.txt',  # Adjust template path
            {'appointment': appointment}
        )
        body = render_to_string(
            'appointments/confirmation_emails/confirmation_email_body.txt',  # Adjust template path
            {'appointment': appointment, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [customer_email])
        messages.success(request, f'Appointment confirmed! A confirmation email has been sent to {appointment.email}.',extra_tags='bag_related=False')

    except Exception as e:  
        messages.error(request, f'There was an error sending the confirmation email: {e}')



    return render(request, 'appointments/success.html', {'appointment': appointment,'qr_code_data': qr_code_data})



@login_required(login_url='/accounts/login/') 
def book_appointment(request):
    """
    Handles the booking of a new dental appointment.

    This view function:
    1. Renders the appointment booking form with available fees.
    2. Processes the form submission, validating the data.
    3. Assigns a random dentist who offers the selected service (if available).
    4. Checks for conflicting appointments with the chosen dentist and time.
    5. Saves the appointment if no conflicts are found.
    6. Redirects to a success page or re-renders the form with errors.

    If the user is authenticated, it also attempts to prefill the 'full_name' field from their last appointment.

    Args:
        request: The HttpRequest object representing the current request.

    Returns:
        HttpResponse: An HTTP response containing either:
            - The rendered appointment booking form (on GET request or invalid POST data).
            - A redirect to a success page (on successful appointment booking).
    """
    fees = Fee.objects.all()
    if request.method == 'POST':
        form = AppointmentForm(request.POST) 
        if form.is_valid():
            
            appointment = form.save(commit=False)
            appointment.user = request.user

                # Get selected service
            selected_fee = form.cleaned_data['service']

                # Get all dentists who offer the selected service
                #available_dentists = Dentist.objects.filter(services__service=selected_fee.service)
            available_dentists = Dentist.objects.filter(services=selected_fee)


            # If there are available dentists, randomly choose one
            if available_dentists.exists():
                appointment.dentist = random.choice(available_dentists)
            else:
                messages.error(request, "No dentists are available for this service at the moment.")
                return render(request, 'appointments/book_appointment.html', {'form': form, 'fees': fees})

            # Check for existing appointment at the same time and dentist
            try:
                existing_appointment = Appointment.objects.get(
                    dentist=appointment.dentist,
                    date=form.cleaned_data['date'],
                    time=form.cleaned_data['time']
                )
                messages.error(request, "This time slot is already booked. Please choose another time.")
                return render(request, 'appointments/book_appointment.html', {'form': form, 'fees': fees})
            except Appointment.DoesNotExist:
                pass  # No conflict, proceed with booking

            appointment.save()  
            return redirect('success', appointment_id=appointment.id)
    else:
        
        initial_data = {}
        if request.user.is_authenticated:
            

            initial_data['email'] = request.user.email
            try:
                # Get the latest appointment for the user
                #previous_appointment = Appointment.objects.filter(email=request.user.email).order_by('-date', '-time').first()
                #latest_appointment = Appointment.objects.filter(user=request.user).latest('date')  # Filter by user object
                latest_appointment = Appointment.objects.filter(user=request.user).latest('date')
                initial_data['full_name'] = latest_appointment.full_name

                # If a previous appointment exists, prefill the full name field
                
                #initial_data['full_name'] = previous_appointment.full_name
                
            except Appointment.DoesNotExist:
                initial_data['full_name'] = ""
                

        form = AppointmentForm(initial=initial_data)

    context = {'fees': fees, 'form': form}
    return render(request, 'appointments/book_appointment.html', context)

