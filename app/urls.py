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
    path('booking/', include('booking.urls')),
    #Account update ko can thiet vi da co CRUD
    # path('account_update/<int:pk>/', AccountUpdateAPIView.as_view(), name='account-update'),
    # search
    path('search_doctor666/', DoctorSearch666View.as_view()),
    path('search_hospital666/', HospitalSearch666View.as_view()),
    path('search_specialty666/', SpecialtySearch666View.as_view()),
    path('search_service666/', ServiceSearch666View.as_view()),
    
    path('search_doctor/', DoctorSearchView.as_view()),
    path('search_hospital/', HospitalSearchView.as_view()),
    path('search_specialty/', SpecialtySearchView.as_view()),
    path('search_service/', ServiceSearchView.as_view()),
    path('search_blog/', BlogSearchView.as_view(), name='search_blog'),

    # account
    path('accounts/<int:pk>/change_password', UserPasswordUpdateAPIView.as_view(), name='user-change-password'),
    
    # user
    path('deleteusers/', DeleteUsers.as_view(), name='deleteusers'),

    # admin
    path('deleteadmins/', DeleteAdmins.as_view(), name='deleteadmins'),

    # doctor
    path('deletedoctors/', DeleteDoctors.as_view(), name='deletedoctors'),

    # hospital
    path('deletehospitals/', DeleteHospitals.as_view(), name='deletehospitals'),

    # specialty
    path('deletespecialties/', DeleteSpecialties.as_view(), name='deletespecialties'),

    # service
    path('deleteservices/', DeleteServices.as_view(), name='deleteservices'),

    # schedule
    path('deleteschedules/', DeleteSchedules.as_view(), name='deleteschedules'),

    # servicedoctor
    path('deleteservicedoctors/', DeleteServiceDoctors.as_view(), name='deleteservicedoctors'),

    # specialtydoctor
    path('deletespecialtydoctors/', DeleteSpecialtyDoctors.as_view(), name='deletespecialtydoctors'),

    # scheduledoctor
    path('getschedulerdoctor/', GetSchedulerDoctor.as_view(), name='getscheduler'),
    path('addschedulerdoctors/', AddSchedulerDoctors.as_view(), name='addschedulers'),
    path('deleteschedulerdoctors/', DeleteSchedulerDoctors.as_view(), name='deleteschedulers'),

    # appointment
    path('appointmentsbyuser/', GetAppointment.as_view(), name='getappointment'),
    path('ratingappointment/<int:pk>/', RatingAppointment.as_view(), name='ratingappointment'),
    path('statusappointment/<int:pk>/', StatusAppointment.as_view(), name='statusappointment'),

    # tool
    path('deletetools/', DeleteTools.as_view(), name='deletetools'),

    # blog
    path('deleteblogs/', DeleteBlogs.as_view(), name='deleteblogs'),

    # category
    path('deletecategories/', DeleteCategories.as_view(), name='deletecategories'),


    # statistical
    path('statisticalAppointment/', statisticalAppointmentAPIView.as_view(), name='statistical'),
    path('statisticalTopDoctor/', statisticalTopDoctorAPIView.as_view(), name='statisticaltopdoctor'),
    path('statisticalTopUser/', statisticalTopUserAPIView.as_view(), name='statisticaltopuser'),

    path('statisticalBlog/', statisticalBlogAPIView.as_view(), name='statisticalblog'),
    path('topCategory/', statisticalTopCategoryAPIView.as_view(), name='topcategory'),
    path('topDoctorBlog/', statisticalTopDoctorBlogAPIView.as_view(), name='topdoctorblog'),

    path('test/', TestAPIView.as_view(), name='test'),
    path('', include(router.urls)),
]
