from django.urls import path
from . import views
from django.views.generic import TemplateView
urlpatterns = [
    path('add_review/', views.add_review, name='add_review'),
    path('', views.display_reviews, name='reviews'),
    path('reviews/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='edit_review'),  # New
    path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='delete_review'), # New
    #path('order_history/<order_number>/',views.order_history,name="order_history"),
   # path('privacy',views.PrivacyPolicy.as_view(),name="privacy"),
    path('privacy/', TemplateView.as_view(template_name="reviews/privacy.html"),name="privacy"),
]