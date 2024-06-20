from django.shortcuts import render,redirect,reverse,get_object_or_404, HttpResponse

from django.views.decorators.http import require_POST
from django.contrib import messages 
""" from django.urls import reverse """
from .forms import OrderForm,Order
from django.conf import settings
from decouple import config
from appointments.models import Appointment
from .models import OrderLineItem
from products.models import Product
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.utils.http import urlencode
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from .webhook_handler import StripeWH_Handler

from basket.context import bag_contents


import stripe
import json

@require_POST
def cache_checkout_data(request):
    """
    Caches checkout data in the Stripe PaymentIntent's metadata.

    This view function is triggered after a successful checkout form submission. It stores essential order information, 
    such as the contents of the shopping bag, user preference to save payment information, and the username (if available), 
    in the metadata of the Stripe PaymentIntent object. This data is useful for later processing and record-keeping.

    Args:
        request: The HttpRequest object representing the current request. It expects the request to contain:
            - 'client_secret': The client secret of the Stripe PaymentIntent.
            - 'save_info': A boolean indicating whether the user wants to save payment information.

    Returns:
        HttpResponse: An HTTP response with status 200 on success or status 400 on failure.
            - If successful, an empty response with status 200 is returned.
            - If there's an exception, an HttpResponse with status 400 and the error message is returned.
    """

    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)




# Create your views here.
def checkout(request):
    """
    Handles the checkout process for user orders.

    This view function performs the following tasks:
    1. Retrieves Stripe keys for payment processing.
    2. Processes the order form data if submitted via POST:
        - Validates the form.
        - Creates a Stripe PaymentIntent.
        - Saves the order and associated order line items.
        - Stores order data in Stripe metadata.
        - Redirects to a success page or displays error messages.
    3. If not a POST request:
        - Retrieves the user's shopping bag.
        - Calculates the order total.
        - Creates a Stripe PaymentIntent.
        - Attempts to pre-fill the order form with user profile data if available.
        - Renders the checkout template with the form, Stripe keys, and context data.

    Args:
        request: The HttpRequest object representing the current request.

    Returns:
        HttpResponse: An HTTP response containing either:
            - The rendered checkout template (with the order form and relevant data).
            - A redirect to the checkout success page (upon successful order placement).
            - A redirect back to the shopping bag (if the bag is empty).
            """
    stripe_public_key = settings.STRIPE_PUBLISHER_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)

            # Get the bag contents to calculate totals
            bag_data = bag_contents(request)
            order.order_total = bag_data['total']
            order.delivery_cost = bag_data['delivery']
            order.grand_total = bag_data['grand_total']

            order.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=item_data,
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_basket'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                latest_order_with_name = Order.objects.filter(user_profile=profile, full_name__isnull=False).order_by('-date').first()
        
                full_name = profile.user.get_full_name()
                if not full_name and latest_order_with_name:
                    full_name = latest_order_with_name.full_name
                order_form = OrderForm(initial={
                    'full_name': full_name,
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    next_url = reverse('checkout')  # URL of the checkout page
    login_url = f"{reverse('account_login')}?{urlencode({'next': next_url})}"
    register_url = f"{reverse('account_signup')}?{urlencode({'next': next_url})}"

    template = 'pay/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'login_url': login_url,
        'register_url': register_url,
    }

    return render(request, template, context)

def checkout_success(request, order_number):

    print( request.session.get('bag', {}))
    
    """
    
    Handles the post-checkout success page and related actions.

    This view function:
    1. Retrieves the order details based on the `order_number`.
    2. If the user is authenticated, it associates the order with their user profile and optionally saves their shipping information.
    3. Sends a success message to the user.
    4. Clears the shopping bag from the session.
    5. Triggers a Stripe webhook handler (if applicable).
    6. Sends a confirmation email to the customer.
    7. Renders the checkout success template with the order details.

    Args:
        request: The HttpRequest object representing the current request.
        order_number: The unique order number of the successful order.

    Returns:
        HttpResponse: An HTTP response containing the rendered checkout success template.
    """
    
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    print(f'Order Total: {order.order_total}, Delivery: {order.delivery_cost}, Grand Total: {order.grand_total}')


    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    order_line_items = OrderLineItem.objects.filter(order=order)
    for item in order_line_items:
        product = item.product
        product.stock -= item.quantity #reduce item stock quantity
        product.save()


    #if 'bag' in request.session:
        #del request.session['bag']
    wh_handler = StripeWH_Handler(request)
    wh_handler.send_confirmation_email(order)  

    #email

     # Send Confirmation Email
    try:
        customer_email = order.email
        subject = render_to_string(
            'pay/confirmation_emails/confirmation_email_subject.txt',
            {'order': order}
        )
        body = render_to_string(
            'pay/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [customer_email])

    except Exception as e:  # Add error handling 
        messages.error(request, f'There was an error sending the confirmation email: {e}')

    #email end 

    template = 'pay/checkout_success.html'
    context = {
        'order': order,
        
    }
    if 'bag' in request.session:
        del request.session['bag']

    return render(request, template, context)

