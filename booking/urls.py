from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingView.as_view(), name='booking'),
]