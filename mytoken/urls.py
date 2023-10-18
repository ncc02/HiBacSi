from django.urls import path
from . import views

urlpatterns = [
    path("refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    # path("/", views.LoginView.as_view(), name="login"),
]