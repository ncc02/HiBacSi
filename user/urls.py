from django.urls import path
from . import views

urlpatterns = [
    path("ListCreate/", views.ListCreateUserView.as_view(), name="LCUser"),
    path("RUDUser/", views.RetrieveUpdateDestroyUserView.as_view(), name="RUDUser"),
]