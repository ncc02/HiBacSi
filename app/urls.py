from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'accounts', AccountViewSet)
router.register(r'users', UserViewSet)
router.register(r'admins', AdminViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'hospitals', HospitalViewSet)
router.register(r'specialties', SpecialtyViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'servicedoctors', ServiceDoctorViewSet)
router.register(r'tools', ToolViewSet)

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('', include(router.urls)),
    # path('login/', LoginView.as_view(), name='login'),
    # path('register/user/', RegisterUser.as_view(), name='register_user'),
    # ...
]
