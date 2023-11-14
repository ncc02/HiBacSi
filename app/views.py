from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Account
from app.permissions import IsAdminPermission, IsDoctorPermission, IsHospitalPermission, IsUserPermission
import app.utils as utils
from rest_framework.decorators import authentication_classes, permission_classes
# from django.conf import settings
# import jwt
import app.utils as utils
import os

import datetime
def print_log(message):
    log_file_path = os.path.join(settings.BASE_DIR, 'log.txt')
    with open(log_file_path, 'a') as log_file:
        log_file.write(str(datetime.datetime.now()) + '\n' + message + '\n\n')
    pass

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


@authentication_classes([])
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        print_log("partial_update")

        if 'avatar' in request.data:
            # Xóa ảnh cũ
            print_log("xoa anh cu")

            if instance.avatar:
                path = instance.avatar.path
                print_log(f"Removing old image. Path: {path}, Media Root: {settings.MEDIA_ROOT}")
                if os.path.isfile(os.path.join(settings.MEDIA_ROOT, path)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, path))

            # Lưu ảnh mới
            instance.avatar = request.data['avatar']
            print_log(f"Anh moi dc luu tai Path: {instance.avatar.path}")
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@authentication_classes([])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params

        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}

        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model User nếu không thì báo lỗi
            if param in [field.name for field in User._meta.get_fields()]:
                filter_kwargs[param] = value
        
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)

        return queryset

@authentication_classes([]) 
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

@authentication_classes([])
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params

        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}

        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model Doctor nếu không thì báo lỗi
            if param in [field.name for field in Doctor._meta.get_fields()]:
                filter_kwargs[param] = value
        
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)

        return queryset


@authentication_classes([]) 
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    # def list(self, request, *args, **kwargs):
    #     hospital = Hospital.objects.all()
    #     content = {
    #         **HospitalSerializer(hospital).data,
    #         'account': AccountSerializer(hospital.account).data
    #     }
    #     return Response(content, status=status.HTTP_200_OK)

    def read(self, request, *args, **kwargs):
        hospital = Hospital.objects.get(id = kwargs['pk'])
        # serializer = HospitalSerializer(hospital)
        content = {
            **HospitalSerializer(hospital).data,
            'account': AccountSerializer(hospital.account).data
        }
        return Response(content, status=status.HTTP_200_OK)

@authentication_classes([])
class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

@authentication_classes([])
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

@authentication_classes([])
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        days_of_week = data['days_of_week']
        time_start = data['start']
        time_end = data['end']
        if (Schedule.objects.filter(days_of_week=days_of_week, start=time_start, end=time_end).exists()):
            return Response({'detail': 'schedule is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

@authentication_classes([])
class SchedulerDoctorViewSet(viewsets.ModelViewSet):
    queryset = Scheduler_Doctor.objects.all()
    serializer_class = SchedulerDoctorSerializer
    # create
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        print(data['doctor_id'])
        data['id_doctor'] = Doctor.objects.get(id = data['doctor_id'])
        data['id_schedule'] = Schedule.objects.get(id = data['schedule_id'])
        if (data['id_doctor'] == None or data['id_schedule'] == None):
            return Response({'detail': 'no find doctor or schedule'}, status=status.HTTP_400_BAD_REQUEST)
        if (Scheduler_Doctor.objects.filter(doctor=data['id_doctor'], schedule=data['id_schedule']).exists()):
            return Response({'detail': 'schedule_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        schedule_doctor = Scheduler_Doctor.objects.create(doctor=data['id_doctor'], schedule=data['id_schedule'])
        schedule_doctor.save()
        serializer = SchedulerDoctorSerializer(schedule_doctor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}
        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model Scheduler_Doctor nếu không thì báo lỗi
            abc = [field.name for field in Scheduler_Doctor._meta.get_fields()]
            if param in [field.name for field in Scheduler_Doctor._meta.get_fields()]:
                filter_kwargs[param] = value
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)
        
        return queryset

@authentication_classes([])
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

@authentication_classes([])
class ServiceDoctorViewSet(viewsets.ModelViewSet):
    queryset = ServiceDoctor.objects.all()
    serializer_class = ServiceDoctorSerializer

@authentication_classes([])
class SpecialtyDoctorViewSet(viewsets.ModelViewSet):
    queryset = SpecialtyDoctor.objects.all()
    serializer_class = SpecialtyDoctorSerializer
    # create
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            data['specialty'] = Specialty.objects.get(id = data['specialty_id'])
        except:
            data['specialty'] = None
        try:
            data['doctor'] = Doctor.objects.get(id = data['doctor_id'])
        except:
            data['doctor'] = None
        if (data['specialty'] == None or data['doctor'] == None):
            return Response({'detail': 'no find specialty or doctor'}, status=status.HTTP_400_BAD_REQUEST)
        if (SpecialtyDoctor.objects.filter(specialty=data['specialty'], doctor=data['doctor']).exists()):
            return Response({'detail': 'specialty_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        specialty_doctor = SpecialtyDoctor.objects.create(specialty=data['specialty'], doctor=data['doctor'])
        specialty_doctor.save()
        serializer = SpecialtyDoctorSerializer(specialty_doctor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@authentication_classes([])
class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer


from django.conf import settings
from rest_framework import generics


# class PasswordUpdateAPIView(generics.UpdateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = UserPasswordUpdateSerializer
#     #permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, *args, **kwargs):
#         instance = self.get_object()
#         oldpassword = request.data.get('oldpassword')
#         newpassword = make_password(request.data.get('password'))
#         if check_password(oldpassword, instance.password):
#             instance.password = newpassword
#             instance.save(update_fields=['password'])
#             serializer = self.get_serializer(instance)
#             return Response({'message': 'Password Changed'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'Incorrect Old Password'}, status=status.HTTP_400_BAD_REQUEST)
