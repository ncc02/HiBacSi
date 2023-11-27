from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Account
from app.permissions import IsAdminPermission, IsDoctorPermission, IsHospitalPermission, IsUserPermission
import app.utils as utils
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView
from hibacsi.pagination import CustomLimitOffsetPagination
from authentication.backends import JWTAuthentication
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
        try:
            data['id_doctor'] = Doctor.objects.get(id = data['doctor_id'])
            data['id_schedule'] = Schedule.objects.get(id = data['schedule_id'])
        except:
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
            if param in [field.name for field in Scheduler_Doctor._meta.get_fields()]:
                filter_kwargs[param] = value
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)
        
        return queryset
    
#create GetSchedulerDoctor
@authentication_classes([])
class GetSchedulerDoctor(GenericAPIView):
    serializer_class = SchedulerDoctorSerializer
    def get(self, request, *args, **kwargs):
        print("get")
        # get doctor
        doctor_id = request.query_params.get('doctor')
        print('doctor_id: ', doctor_id)
        schedule_doctor = Scheduler_Doctor.objects.filter(doctor=doctor_id)
        # chia schedule_doctor thanh 3 list theo morning, afternoon, evening
        print(2)
        morning = []
        afternoon = []
        evening = []
        for i in schedule_doctor:
            if i.schedule.end.hour < 12:
                morning.append(i.schedule)
            if i.schedule.start.hour >= 12 and i.schedule.end.hour < 18:
                afternoon.append(i.schedule)
            if i.schedule.start.hour >= 18:
                evening.append(i.schedule)
        print(morning)
        print(afternoon)
        print(evening)
        serializer_data = {
            'morning': ScheduleSerializer(morning, many=True).data,
            'afternoon': ScheduleSerializer(afternoon, many=True).data,
            'evening': ScheduleSerializer(evening, many=True).data,
        }
        serializer = GetSchedulerSerializer(serializer_data)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
# create GetAppointment
@permission_classes([IsUserPermission])
class GetAppointment(GenericAPIView):
    serializer_class = AppointmentSerializer
    def get(self, request, *args, **kwargs):
        print(1)
        # get user by account
        user = User.objects.get(account=request.account)
        # get appointment by user
        appointment = Appointment.objects.filter(user=user)
        # chia appointment thanh 3 list là appointment sắp đến, appointment chưa xác nhận, appointment đã xác nhận
        appointment_coming = []
        appointment_not_confirm = []
        appointment_confirmed = []
        for i in appointment:
            if i.date > datetime.date.today():
                appointment_coming.append(i)
            if i.status == 0:
                appointment_not_confirm.append(i)
            if i.status == 1:
                appointment_confirmed.append(i)
        print(appointment_coming)
        print(appointment_not_confirm)
        print(appointment_confirmed)
        serializer_data = {
            'coming': AppointmentSerializer(appointment_coming, many=True).data,
            'not_confirm': AppointmentSerializer(appointment_not_confirm, many=True).data,
            'confirmed': AppointmentSerializer(appointment_confirmed, many=True).data,
        }
        print(2)
        serializer = GetAppointmentSerializer(serializer_data)
        print(3)
        return Response(serializer.data, status=status.HTTP_200_OK)

# create RatingAppointment
@permission_classes([IsUserPermission])
class RatingAppointment(GenericAPIView):
    serializer_class = AppointmentSerializer
    def post(self, request, *args, **kwargs):
        # kiểm tra user có phải là user của appointment   
        user = User.objects.get(account=request.account)
        appointment = Appointment.objects.get(id=kwargs['pk'])
        if (user != appointment.user):
            return Response({'detail': 'user is not user of appointment'}, status=status.HTTP_400_BAD_REQUEST)
        # update rating cho bác sĩ
        if (appointment.rating == 0):
            doctor = appointment.schedule_doctor.doctor
            doctor.num_of_rating += 1
            try:
                rating_value = float(request.data['rating'])
            except KeyError:
                return Response({'detail': 'rating is not exist'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                rating_value = 0.0
            doctor.rating = (doctor.rating * (doctor.num_of_rating - 1) + rating_value) / doctor.num_of_rating
            doctor.save()
        else:
            return Response({'detail': 'appointment has been rated'}, status=status.HTTP_400_BAD_REQUEST)
        # update rating cho appointment
        appointment.rating = rating_value
        appointment.save()
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# create StatusAppointment 
@permission_classes([IsUserPermission | IsDoctorPermission])
class StatusAppointment(GenericAPIView):
    serializer_class = AppointmentSerializer
    def post(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(account=request.account)
            appointment = Appointment.objects.get(id=kwargs['pk'])
            if (doctor != appointment.schedule_doctor.doctor):
                return Response({'detail': 'doctor is not doctor of appointment'}, status=status.HTTP_400_BAD_REQUEST)
        except Doctor.DoesNotExist:
            user = User.objects.get(account=request.account)
            appointment = Appointment.objects.get(id=kwargs['pk'])
            if (user != appointment.user):
                return Response({'detail': 'user is not user of appointment'}, status=status.HTTP_400_BAD_REQUEST)
        # update status cho appointment
        try:
            appointment.status = request.data['status']
        except KeyError:
            return Response({'detail': 'status is not exist'}, status=status.HTTP_400_BAD_REQUEST)
        appointment.save()
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

# @authentication_classes([])
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    # get queryset by user_id
    def get_queryset(self):
        print(1)
        queryset = self.queryset
        params = self.request.query_params
        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}
        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model Appointment nếu không thì báo lỗi
            if param in [field.name for field in Appointment._meta.get_fields()]:
                filter_kwargs[param] = value
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)
        return queryset

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
    
    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}
        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model SpecialtyDoctor nếu không thì báo lỗi
            if param in [field.name for field in SpecialtyDoctor._meta.get_fields()]:
                filter_kwargs[param] = value
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs 
        queryset = queryset.filter(**filter_kwargs)

        return queryset

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

from rest_framework.pagination import PageNumberPagination
class CustomPagination(PageNumberPagination):
    page_size = 6

class CustomPagination2(PageNumberPagination):
    page_size = 2

@authentication_classes([])
class SearchAllAPIView(APIView):   

    def get(self, request):
        name = request.query_params.get('name', '')
        address = request.query_params.get('address', '')

        doctors = Doctor.objects.filter(name__icontains=name, address__icontains=address)
        hospitals = Hospital.objects.filter(name__icontains=name, address__icontains=address)
        
        specialtys = Specialty.objects.filter(name__icontains=name)
        services = Service.objects.filter(name__icontains=name)
        

        paginator = CustomPagination2()
        paginated_doctors = paginator.paginate_queryset(doctors, request)
        doctor_serializer = DoctorSerializer(paginated_doctors, many=True)
        
        paginated_hospitals = paginator.paginate_queryset(hospitals, request)
        hospital_serializer = HospitalSerializer(paginated_hospitals, many=True)
        
        paginated_specialtys = paginator.paginate_queryset(specialtys, request)
        specialty_serializer = SpecialtySerializer(paginated_specialtys, many=True)
        
        paginated_services = paginator.paginate_queryset(services, request)
        services_serializer = ServiceSerializer(paginated_services, many=True)
        

        # doctor_serializer = DoctorSerializer(doctors, many=True)
        # hospital_serializer = HospitalSerializer(hospitals, many=True)
        # specialty_serializer = SpecialtySerializer(specialtys, many=True)
        # services_serializer = ServiceSerializer(services, many=True)
        
        # # Đếm số lượng đối tượng trong mỗi danh sách
        # count_doctors = len(doctor_serializer.data)
        # count_hospitals = len(hospital_serializer.data)
        # count_specialtys = len(specialty_serializer.data)
        # count_services = len(services_serializer.data)

        response_data = {
            # 'count_doctors': count_doctors,
            # 'count_hospitals': count_hospitals,
            # 'count_specialtys': count_specialtys,
            # 'count_services': count_services,
            'doctors': doctor_serializer.data,
            'hospitals': hospital_serializer.data,
            'specialtys': specialty_serializer.data,
            'services': services_serializer.data,
            
        }

        return paginator.get_paginated_response(response_data)


@authentication_classes([])
class SearchDoctorAPIView(APIView):
    
    def get(self, request): 
        name = request.query_params.get('name', '')
        address = request.query_params.get('address', '')
        specialty = request.query_params.get('specialty', '')
        service = request.query_params.get('service', '')

        # Bỏ điều kiện lọc cho specialty nếu specialty không được cung cấp
        specialty_filter = {} if not specialty else {'specialtydoctor__specialty__name__iexact': specialty}

        # Bỏ điều kiện lọc cho service nếu service không được cung cấp
        service_filter = {} if not service else {'servicedoctor__service__name__iexact': service}

        doctors = Doctor.objects.filter(
            name__icontains=name,
            address__icontains=address,
            **specialty_filter,
            **service_filter,
        )

        # hospitals = Hospital.objects.filter(
        #     name__icontains=name,
        #     address__icontains=address,
        #     specialtydoctor__specialty__name__iexact=specialty,
        #     servicedoctor__service__name__iexact=service,
        # )
        paginator = CustomPagination()
        paginated_doctors = paginator.paginate_queryset(doctors, request)
        doctor_serializer = DoctorSerializer(paginated_doctors, many=True)
        # hospital_serializer = HospitalSerializer(hospitals, many=True)
        # count_doctors = len(doctor_serializer.data)
        
        response_data = {
            'doctors': doctor_serializer.data,
            # 'hospitals': hospital_serializer.data,
        }
        return paginator.get_paginated_response(response_data)
        
        # return Response(response_data, status=status.HTTP_200_OK)
    