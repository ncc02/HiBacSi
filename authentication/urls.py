from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/user/", views.RegisterView.as_view(), name="register"),
    path("register/admin/", views.RegisterViewAdmin.as_view(), name="register_admin"),
    path("register/doctor/", views.RegisterViewDoctor.as_view(), name="register_admin"),
    path("register/hospital/", views.RegisterViewHospital.as_view(), name="register_admin"),
]