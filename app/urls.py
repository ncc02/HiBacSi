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
router.register(r'blogs', BlogViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'blogcruds', BlogCRUDViewSet)

urlpatterns = [
    path('token/', include('mytoken.urls')),
    path('auth/', include('authentication.urls')),
    path('user/', include('user.urls')),
    path('booking/', include('booking.urls')),
    #Account update ko can thiet vi da co CRUD
    # path('account_update/<int:pk>/', AccountUpdateAPIView.as_view(), name='account-update'),

    path('search_doctor666/', DoctorSearch666View.as_view()),
    path('search_hospital666/', HospitalSearch666View.as_view()),
    path('search_specialty666/', SpecialtySearch666View.as_view()),
    path('search_service666/', ServiceSearch666View.as_view()),
    
    path('search_doctor/', DoctorSearchView.as_view()),
    path('search_hospital/', HospitalSearchView.as_view()),
    path('search_specialty/', SpecialtySearchView.as_view()),
    path('search_service/', ServiceSearchView.as_view()),
    path('search_blog/', BlogSearchView.as_view(), name='search_blog'),
    path('accounts/<int:pk>/change_password', UserPasswordUpdateAPIView.as_view(), name='user-change-password'),
    
    path('getschedulerdoctor/', GetSchedulerDoctor.as_view(), name='getscheduler'),
    path('appointmentsbyuser/', GetAppointment.as_view(), name='getappointment'),
    path('ratingappointment/<int:pk>/', RatingAppointment.as_view(), name='ratingappointment'),
    path('statusappointment/<int:pk>/', StatusAppointment.as_view(), name='statusappointment'),

    path('test/', TestAPIView.as_view(), name='test'),
    path('', include(router.urls)),
]
