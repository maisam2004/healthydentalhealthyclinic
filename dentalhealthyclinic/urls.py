"""dentalhealthyclinic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static

from django.conf.urls import handler404
from .error_handlers import Error404View,ForbiddenView

handler403 = ForbiddenView.as_view()
handler404 = Error404View.as_view()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('appointments/', include('appointments.urls')),
    path('contact/', include('contact.urls')),
    path('products/', include('products.urls')),
    path('basket/', include('basket.urls')),
    path('dservices/', include('dservices.urls')),
    path('pay/', include('pay.urls')),
    path('profiles/', include('profiles.urls')),
    path('fee/', include('fee.urls')),
    path('reviews/', include('reviews.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)