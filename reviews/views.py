from django.shortcuts import render
from .models import Review
from .forms import ReviewForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from .models import Review
from django.views.generic import UpdateView, DeleteView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin



def display_reviews(request):
    reviews = Review.objects.all()
    context = {
        'reviews': reviews
    }
    return render(request, 'reviews/reviews.html', context) 




@login_required
def add_review(request):

    """
    Handles the creation and submission of user reviews.

    This view function:

    1. If the request is a POST:
        - Initializes a ReviewForm with the user's information, data, and any uploaded files.
        - If the form is valid:
            - Saves the review, associating it with the logged-in user.
            - Displays a success message.
            - Redirects the user to the reviews list view.
        - If the form is invalid:
            - Adds error messages for each field with validation issues.
    2. If the request is a GET:
        - Initializes a blank ReviewForm for the logged-in user.

    Args:
        request: The HttpRequest object representing the current request.

    Returns:
        HttpResponse: An HTTP response containing either:
            - The rendered add review form (on GET or invalid POST).
            - A redirect to the reviews list view (on successful submission).
    """

    if request.method == 'POST':
        form = ReviewForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('reviews')  # Adjust the redirect to your reviews list view
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    message = f"Error in {field}: {error}"
                    messages.add_message(request, messages.ERROR, message, extra_tags='toast')
    else:
        form = ReviewForm(user=request.user)

    return render(request, 'reviews/add_review.html', {'form': form})




class ReviewUpdateView(LoginRequiredMixin, UpdateView):

    """
    Handles the updating of existing reviews.

    This class-based view allows logged-in users to edit their reviews. It uses a ReviewForm to 
    present the review fields and ensures that only the review's owner can modify it.

    Attributes:
        model: The Review model that this view operates on.
        form_class: The ReviewForm class to use for the form.
        template_name: The name of the template to use for rendering the edit review form.
        success_url: The URL to redirect to upon successful update.

    Methods:
        get_form_kwargs(): Passes the current user to the form constructor.
        form_valid(form): Displays a success message and calls the parent class's form_valid method.
    """

    model = Review
    form_class = ReviewForm
    template_name = 'reviews/edit_review.html'  # Create this template
    success_url = '/reviews/'
    def get_form_kwargs(self):
        """Pass the request.user to the form's constructor."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, "The Review was Edited successfully.")
        return super(ReviewUpdateView,self).form_valid(form)

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    context_object_name = 'review'
    success_url = '/reviews/'
    def form_valid(self, form):
        messages.success(self.request, "The review was deleted successfully.",extra_tags='bag_related=False')
        return super(ReviewDeleteView,self).form_valid(form)
    

