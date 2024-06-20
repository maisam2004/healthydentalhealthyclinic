from django.shortcuts import render,get_object_or_404
from .models import User,UserProfile,ProfilePicture

from appointments.models import Appointment
from .forms import UserProfileForm,ProfilePictureForm
from django.contrib import messages 
from pay.models import Order
from django.contrib.auth.decorators import login_required



from .forms import UserProfileForm, ProfilePictureForm
from .models import ProfilePicture


@login_required
def profile(request):
    """
    Displays the user's profile page.

    This view function:
    1. Retrieves the user's profile and profile picture information.
    2. Creates forms for updating the profile and profile picture.
    3. Handles POST requests to update either the profile picture or the profile details.
        - Validates the submitted forms.
        - Saves changes to the database if valid.
        - Displays appropriate success or error messages.
    4. Retrieves the user's past orders and appointments.
    5. Renders the profile template, passing the profile data, forms, orders, appointments, and other context.

    Args:
        request: The HttpRequest object representing the current request.

    Returns:
        HttpResponse: An HTTP response containing the rendered profile template with user-specific data.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    profile_picture, created = ProfilePicture.objects.get_or_create(user=request.user)

    user_form = UserProfileForm(instance=profile)
    picture_form = ProfilePictureForm(instance=profile_picture)

    if request.method == 'POST':
        # Handle profile picture form
        if 'image' in request.FILES:
            picture_form = ProfilePictureForm(request.POST, request.FILES, instance=profile_picture)
            if picture_form.is_valid():
                picture_form.save()
                messages.success(request, 'Profile picture updated successfully')
            else:
                messages.error(request, 'Failed to update profile picture. Please ensure the form is valid.')

        # Handle user profile form
        else:
            user_form = UserProfileForm(request.POST, instance=profile)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profile updated successfully')
            else:
                messages.error(request, 'Failed to update profile. Please ensure the form is valid.')

    orders = profile.orders.all()
    appointments = Appointment.objects.filter(email=request.user.email)
    latest_order_with_name = Order.objects.filter(user_profile=profile, full_name__isnull=False).order_by('-date').first() 

    template = 'profiles/profile.html'
    context = {
        'on_profile_page': profile,
        'user_form': user_form,
        'picture_form': picture_form,
        'orders': orders,
        'user': request.user,
        'appointments': appointments,
        'latest_order_with_name': latest_order_with_name
    }
    return render(request, template, context)

@login_required
def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'pay/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)