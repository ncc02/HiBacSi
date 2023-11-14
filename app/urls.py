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
router.register(r'specialtydoctor', SpecialtyDoctorViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'schedulerdoctor', SchedulerDoctorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'servicedoctors', ServiceDoctorViewSet)
router.register(r'tools', ToolViewSet)

urlpatterns = [
    path('token/', include('mytoken.urls')),
    path('auth/', include('authentication.urls')),
    path('user/', include('user.urls')),
    path('booking/', include('booking.urls')),
    #Account update ko can thiet vi da co CRUD
    # path('account_update/<int:pk>/', AccountUpdateAPIView.as_view(), name='account-update'),
    path('', include(router.urls)),
    path('search_all/', SearchAllAPIView.as_view()),
    path('search_doctor/', SearchDoctorAPIView.as_view()),
    

]
