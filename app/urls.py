from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/user', RegisterUser.as_view(), name='register_user'),
    # ...
]
