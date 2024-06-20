
from django.urls import path,reverse
from . import views


urlpatterns = [
    path('',views.view_basket,name='view_basket'),
    path('add/<item_id>/',views.add_to_basket,name="add_to_bag"),
    path('update_basket/', views.update_basket, name='update_basket'),
]