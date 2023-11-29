from django.urls import path
from . import views

urlpatterns = [
    path("refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", views.TokenVerifyView.as_view(), name="token_verify"),
    # path("/", views.LoginView.as_view(), name="login"),
]