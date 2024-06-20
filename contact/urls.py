
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.contact ,name='contact'),
    path('about',views.AboutTemplateView.as_view(),name="about"),
]