from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Account  
# from django.conf import settings
# import jwt
import app.utils as utils
import os

# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         success = utils.login_success(username=username, password=password)
 
#         if success:
#             # Đăng nhập thành công
#             account = Account.objects.get(username=username)
#             account_data = AccountSerializer(account).data
#             auth_token = utils.generate_access_token(account)
#             response_data = {
#                 'state': True,
#                 'account': account_data,
#                 'token': auth_token
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             # Đăng nhập thất bại
#             response_data = {'state': False, 'message': 'Invalid username or password'}
#             return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


# class RegisterUser(APIView):
#     def post(self, request):
#         data=request.data.copy()
#         data['role'] = 'user'
#         data['password'] = utils.hash_password(data['password'])
#         serializer = AccountSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'state': True, 'message': 'Registration successful.'})
#         else:
#             return Response({'state': False, 'message': serializer.errors})
        


from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class ServiceDoctorViewSet(viewsets.ModelViewSet):
    queryset = ServiceDoctor.objects.all()
    serializer_class = ServiceDoctorSerializer

class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
