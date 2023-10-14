from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('user/', include('user.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('register/user/', RegisterUser.as_view(), name='register_user'),
    # ...
]
