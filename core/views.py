from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseNotFound

def homepage(request):
    """ Renders the homepage of the website.

    This view function handles the rendering of the homepage template. """
    context = {'is_homepage': True,} 

    return render(request, 'core/homepage.html', context)




class NotFoundView(TemplateView):
    """
     Renders a custom 404 Not Found error page.

    This view is designed to handle HTTP 404 errors gracefully by displaying a
    user-friendly template instead of Django's default error page.

    Attributes:
        template_name (str): The path to the template file used to render the
            404 error page.

    Methods:
        get(request, *args, **kwargs): Handles GET requests and returns an
            HttpResponseNotFound object with the rendered 404 template.
"""

    template_name = "core/404.html"  

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


