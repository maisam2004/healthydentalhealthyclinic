
from django.urls import path
from . import views

urlpatterns = [
    path('general',views.GeneralView.as_view() ,name='general'),
    path('cosmetic',views.CosmeticView.as_view() ,name='cosmetic'),
    path('restorative',views.RestoractiveView.as_view() ,name='restorative'),
]