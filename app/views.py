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
class BlogCRUDViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogCRUDSerializer

@authentication_classes([])
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    # def list(self, request, *args, **kwargs): -> DEO CAN
    #     response = super().list(request, *args, **kwargs)

    #     # Serialize and include Category and Doctor data in the response
    #     serialized_categories = CategorySerializer(
    #         set(blog.id_category for blog in self.queryset),
    #         many=True
    #     ).data

    #     serialized_doctors = DoctorSerializer(
    #         set(blog.id_doctor for blog in self.queryset),
    #         many=True
    #     ).data

    #     response.data['categories'] = serialized_categories
    #     response.data['doctors'] = serialized_doctors

    #     return response

@authentication_classes([])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
        # get doctor
        try: 
            doctor_id = request.query_params.get('doctor')
            print('doctor_id: ', doctor_id)
        except KeyError:
            return Response({'detail': 'key "doctor" is require'}, status=status.HTTP_400_BAD_REQUEST)
        schedule_doctor = Scheduler_Doctor.objects.filter(doctor=doctor_id)
        # chia schedule_doctor thanh 3 list theo morning, afternoon, evening
        print(2)
        morning = []
        afternoon = []
        evening = []
        for i in schedule_doctor:
            if i.schedule.end.hour < 12:
                morning.append({'id': i.schedule.id, 'days_of_week': i.schedule.days_of_week, 'start': i.schedule.start, 'end': i.schedule.end})
            if i.schedule.start.hour >= 12 and i.schedule.end.hour < 18:
                afternoon.append({'id': i.schedule.id, 'days_of_week': i.schedule.days_of_week, 'start': i.schedule.start, 'end': i.schedule.end})
            if i.schedule.start.hour >= 18:
                evening.append({'id': i.schedule.id, 'days_of_week': i.schedule.days_of_week, 'start': i.schedule.start, 'end': i.schedule.end})
        
        print(morning)
        print(afternoon)
        print(evening)
        serializer_data = {
            'morning': ScheduleByDoctorSerializer(morning, many=True).data,
            'afternoon': ScheduleByDoctorSerializer(afternoon, many=True).data,
            'evening': ScheduleByDoctorSerializer(evening, many=True).data,
        }
        serializer = GetSchedulerSerializer(data=serializer_data)
        serializer.is_valid()
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)        

# @authentication_classes([])
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

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

        # Check if 'doctor_id' is in the query parameters
        doctor_id = params.get('doctor_id', None)
        if doctor_id:
            # Filter appointments based on the associated doctor's id
            queryset = queryset.filter(schedule_doctor__doctor__id=doctor_id)
            
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
            data['doctor'] = Doctor.objects.get(id = data['doctor_id'])
        except:
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



from rest_framework.pagination import PageNumberPagination
class CustomPagination(PageNumberPagination):
    page_size = 6

class CustomPagination2(PageNumberPagination):
    page_size = 2


@authentication_classes([])
class TestAPIView(APIView):   

    def get(self, request):

        tests = Test.objects.all()
        paginator = CustomPagination2()
        paginated_tests = paginator.paginate_queryset(tests, request)
        test_serializer = TestSerializer(paginated_tests, many=True)
        

        response_data = {
            'total_page':paginator.page.paginator.num_pages,
            'services': test_serializer.data,
        }

        return paginator.get_paginated_response(response_data)


@authentication_classes([])
class BlogSearchView(generics.ListAPIView):
    serializer_class = BlogSerializer
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        id_category = self.request.query_params.get('id_category', None)
        id_doctor = self.request.query_params.get('id_doctor', None)

        queryset = Blog.objects.all()
        
        if name:
            queryset = queryset.filter(title__icontains=name)

        if id_category:
            queryset = queryset.filter(id_category=id_category)

        if id_doctor:
            queryset = queryset.filter(id_doctor=id_doctor)

        # Sử dụng select_related để trả về thông tin của bác sĩ và danh mục cùng với blog
        queryset = queryset.select_related('id_doctor', 'id_category')

        return queryset
    
@authentication_classes([])
class DoctorSearchView(generics.ListAPIView):
    serializer_class = DoctorSerializer  # Corrected serializer class name
    pagination_class = CustomPagination2
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_hospital = self.request.query_params.get('id_hospital', None)  # Corrected parameter name
        id_specialty = self.request.query_params.get('id_specialty', None)
        id_service = self.request.query_params.get('id_service', None)

        queryset = Doctor.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if id_hospital:
            queryset = queryset.filter(hospital__id=id_hospital)  # Corrected filtering by hospital ID

        if id_specialty:
            queryset = queryset.filter(specialtydoctor__specialty__id=id_specialty)  # Corrected filtering by specialty ID

        if id_service:
            queryset = queryset.filter(servicedoctor__service__id=id_service)  # Corrected filtering by service ID

        return queryset

@authentication_classes([])
class HospitalSearchView(generics.ListAPIView):
    serializer_class = HospitalSerializer
    pagination_class = CustomPagination2
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_specialty = self.request.query_params.get('id_specialty', None)
        id_service = self.request.query_params.get('id_service', None)

        queryset = Hospital.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if id_specialty:
            # Filter hospitals based on doctors with the given specialty
            queryset = queryset.filter(doctor__specialtydoctor__specialty__id=id_specialty)

        if id_service:
            # Filter hospitals based on doctors with the given service
            queryset = queryset.filter(doctor__servicedoctor__service__id=id_service)

        return queryset


@authentication_classes([])
class DoctorSearch666View(generics.ListAPIView):
    serializer_class = DoctorSerializer  # Corrected serializer class name
    pagination_class = CustomPagination
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_hospital = self.request.query_params.get('id_hospital', None)  # Corrected parameter name
        id_specialty = self.request.query_params.get('id_specialty', None)
        id_service = self.request.query_params.get('id_service', None)

        queryset = Doctor.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if id_hospital:
            queryset = queryset.filter(hospital__id=id_hospital)  # Corrected filtering by hospital ID

        if id_specialty:
            queryset = queryset.filter(specialtydoctor__specialty__id=id_specialty)  # Corrected filtering by specialty ID

        if id_service:
            queryset = queryset.filter(servicedoctor__service__id=id_service)  # Corrected filtering by service ID

        return queryset

@authentication_classes([])
class HospitalSearch666View(generics.ListAPIView):
    serializer_class = HospitalSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_specialty = self.request.query_params.get('id_specialty', None)
        id_service = self.request.query_params.get('id_service', None)

        queryset = Hospital.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if id_specialty:
            # Filter hospitals based on doctors with the given specialty
            queryset = queryset.filter(doctor__specialtydoctor__specialty__id=id_specialty)

        if id_service:
            # Filter hospitals based on doctors with the given service
            queryset = queryset.filter(doctor__servicedoctor__service__id=id_service)

        return queryset

@authentication_classes([])
class SpecialtySearchView(generics.ListAPIView):
    serializer_class = SpecialtySerializer
    pagination_class = CustomPagination2
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_doctor = self.request.query_params.get('id_doctor', None)
        id_hospital = self.request.query_params.get('id_hospital', None)
             
        queryset = Specialty.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(specialtydoctor__doctor__city__icontains=city)

        if id_doctor:
            queryset = queryset.filter(specialtydoctor__doctor__id=id_doctor)

        if id_hospital:
            queryset = queryset.filter(specialtydoctor__doctor__hospital__id=id_hospital)
        return queryset

@authentication_classes([])
class SpecialtySearch666View(generics.ListAPIView):
    serializer_class = SpecialtySerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_doctor = self.request.query_params.get('id_doctor', None)
        id_hospital = self.request.query_params.get('id_hospital', None)
             
        queryset = Specialty.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(specialtydoctor__doctor__city__icontains=city)

        if id_doctor:
            queryset = queryset.filter(specialtydoctor__doctor__id=id_doctor)

        if id_hospital:
            queryset = queryset.filter(specialtydoctor__doctor__hospital__id=id_hospital)
        return queryset

@authentication_classes([])
class ServiceSearchView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    pagination_class = CustomPagination2
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_doctor = self.request.query_params.get('id_doctor', None)
        id_hospital = self.request.query_params.get('id_hospital', None)

        queryset = Service.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(servicedoctor__doctor__city__icontains=city)

        if id_doctor:
            queryset = queryset.filter(servicedoctor__doctor__id=id_doctor)

        if id_hospital:
            queryset = queryset.filter(servicedoctor__doctor__hospital__id=id_hospital)

        return queryset

@authentication_classes([])
class ServiceSearch666View(generics.ListAPIView):
    serializer_class = ServiceSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        city = self.request.query_params.get('city', None)
        id_doctor = self.request.query_params.get('id_doctor', None)
        id_hospital = self.request.query_params.get('id_hospital', None)


        queryset = Service.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(servicedoctor__doctor__city__icontains=city)

        if id_doctor:
            queryset = queryset.filter(servicedoctor__doctor__id=id_doctor)

        if id_hospital:
            queryset = queryset.filter(servicedoctor__doctor__hospital__id=id_hospital)

        return queryset

import hashlib
def hash_password(password):
    salt = "random string to make the hash more secure"
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password


@authentication_classes([])
class UserPasswordUpdateAPIView(generics.UpdateAPIView): #Ten User nhung that ra la Account
    queryset = Account.objects.all()
    serializer_class = UserPasswordUpdateSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        oldpassword = request.data.get('oldpassword')
        newpassword = request.data.get('newpassword')
        if hash_password(oldpassword) == instance.password:
            instance.password = hash_password(newpassword)
            instance.save(update_fields=['password'])
            
            return Response({'message': 'Password Changed', 'newpassword_hash':str(instance.password)}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Incorrect Old Password', 'oldpassword':str(oldpassword),'hash_oldpassword':str(hash_password(oldpassword)),'instance_passwrod': str(instance.password)}, status=status.HTTP_400_BAD_REQUEST)
        
from hibacsi.pagination import CustomLimitOffsetPagination
from authentication.backends import JWTAuthentication

# create GetAppointment
@permission_classes([IsUserPermission])
class GetAppointment(GenericAPIView):
    serializer_class = GetAppointmentSerializer
    def get(self, request, *args, **kwargs):
        print(111)
        # get user by account
        try:
            user = User.objects.get(account=request.account)
        except User.DoesNotExist:
            return Response({'detail': 'user is not exist'}, status=status.HTTP_400_BAD_REQUEST)
        # get appointment by user
        appointment = Appointment.objects.filter(user=user)
        # chia appointment thanh 3 list là appointment sắp đến, appointment chưa xác nhận, appointment đã xác nhận
        appointment_coming = []
        appointment_not_confirm = []
        appointment_confirmed = []
        appointment_cancel = []
        for i in appointment:
            if i.date > datetime.date.today():
                appointment_coming.append(i)
            if i.status == 0:
                appointment_not_confirm.append(i)
            if i.status == 1:
                appointment_confirmed.append(i)
            if i.status == 2:
                appointment_cancel.append(i)

        print(appointment_coming)
        print(appointment_not_confirm)
        print(appointment_confirmed)
        print(appointment_cancel)

        serializer_data = {
            'coming': AppointmentSerializer(appointment_coming, many=True).data,
            'not_confirm': AppointmentSerializer(appointment_not_confirm, many=True).data,
            'confirmed': AppointmentSerializer(appointment_confirmed, many=True).data,
            'cancel': AppointmentSerializer(appointment_cancel, many=True).data
        }
        print(2)
        serializer = GetAppointmentSerializer(data=serializer_data)
        serializer.is_valid()
        print(3)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# create RatingAppointment
@permission_classes([IsUserPermission])
class RatingAppointment(GenericAPIView):
    serializer_class = AppointmentSerializer
    def post(self, request, *args, **kwargs):
        # kiểm tra user có phải là user của appointment   
        try:
            user = User.objects.get(account=request.account)
        except User.DoesNotExist:
            return Response({'detail': 'user is not exist'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            appointment = Appointment.objects.get(id=kwargs['pk'])
        except Appointment.DoesNotExist:
            return Response({'detail': 'appointment is not exist'}, status=status.HTTP_400_BAD_REQUEST)
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

