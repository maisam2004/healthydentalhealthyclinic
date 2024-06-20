from django.views.generic import TemplateView

#class Error404View(TemplateView):
   # template_name = '404.html'

class Error404View(TemplateView):
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

    template_name = "404.html"  

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


class ForbiddenView(TemplateView):
    """
    Renders a custom 403 Forbidden error page.
    """

    template_name = "403.html"
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 403
        return response
    
