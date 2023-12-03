from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
import json
from .models import Account
from app.permissions import IsAdminPermission, IsDoctorPermission, IsHospitalPermission, IsUserPermission
import app.utils as utils
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView
from hibacsi.pagination import CustomLimitOffsetPagination
from authentication.backends import JWTAuthentication
from rest_framework.decorators import action
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
    
    def destroy(self, request, *args, **kwargs):
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
    
    def destroy(self, request, *args, **kwargs):
        # lấy user
        user = self.get_object()
        # lấy account
        account = Account.objects.get(id=user.account.id)
        # lấy appointment 
        appointments = Appointment.objects.filter(user=user)
        print(account)
        print(appointments)
        # thực hiện xoá
        appointments.delete()
        account.delete()
        return Response({'detail': 'Delete success'}, status=status.HTTP_200_OK)

@authentication_classes([]) 
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    def destroy(self, request, *args, **kwargs):
        # lấy admin
        admin = self.get_object()
        # lấy account
        account = Account.objects.get(id=admin.account.id)
        # thực hiện xoá
        account.delete()
        return Response({'detail': 'Delete success'}, status=status.HTTP_200_OK)

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
    
    def destroy(self, request, *args, **kwargs):
        # lấy doctor
        doctor = self.get_object()
        # lấy account
        account = Account.objects.get(id=doctor.account.id)
        # lấy appointment 
        appointments = Appointment.objects.filter(schedule_doctor__doctor=doctor)
        # lấy schedule_doctor
        schedule_doctors = Scheduler_Doctor.objects.filter(doctor=doctor)
        # lấy servicedoctor
        servicedoctors = ServiceDoctor.objects.filter(doctor=doctor)
        # lấy specialtydoctor
        specialtydoctors = SpecialtyDoctor.objects.filter(doctor=doctor)
        print(account)
        print(appointments)
        print(schedule_doctors)
        print(servicedoctors)
        print(specialtydoctors)
        # thực hiện xoá
        appointments.delete()
        schedule_doctors.delete()
        servicedoctors.delete()
        specialtydoctors.delete()
        account.delete()
        return Response({'detail': 'Delete success'}, status=status.HTTP_200_OK)


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
    
    def destroy(self, request, *args, **kwargs):
        # lấy hospital
        hospital = self.get_object()
        # lấy account
        account = Account.objects.get(id=hospital.account.id)
        # lấy doctor
        doctors = Doctor.objects.filter(hospital=hospital)

        print(account)
        print(doctors)
        # thực hiện xoá
        doctors.delete()
        account.delete()
        return Response({'detail': 'Delete success'}, status=status.HTTP_200_OK)

@authentication_classes([])
class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

    def destroy(self, request, *args, **kwargs):
        # lấy specialty
        specialty = self.get_object()
        # lấy specialtydoctor
        specialtydoctors = SpecialtyDoctor.objects.filter(specialty=specialty)
        print(specialtydoctors)
        # thực hiện xoá
        specialtydoctors.delete()
        return super().destroy(request, *args, **kwargs)

@authentication_classes([])
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def destroy(self, request, *args, **kwargs):
        # lấy service
        service = self.get_object()
        # lấy servicedoctor
        servicedoctors = ServiceDoctor.objects.filter(service=service)
        print(servicedoctors)
        # thực hiện xoá
        servicedoctors.delete()
        return super().destroy(request, *args, **kwargs)

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
    
    def destroy(self, request, *args, **kwargs):
        # lấy schedule
        schedule = self.get_object()
        # lấy schedule_doctor
        schedule_doctors = Scheduler_Doctor.objects.filter(schedule=schedule)
        # lấy appointment
        appointments = Appointment.objects.filter(schedule_doctor__schedule=schedule)
        print(schedule)
        print(schedule_doctors)
        print(appointments)
        # thực hiện xoá
        appointments.delete()
        schedule_doctors.delete()
        return super().destroy(request, *args, **kwargs)

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
    
    def destroy(self, request, *args, **kwargs):
        # lấy schedule_doctor
        schedule_doctor = self.get_object()
        # lấy appointment
        appointments = Appointment.objects.filter(schedule_doctor=schedule_doctor)
        print(schedule_doctor)
        print(appointments)
        # thực hiện xoá
        appointments.delete()
        return super().destroy(request, *args, **kwargs)

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

# user
@authentication_classes([])
class DeleteUsers(GenericAPIView):
    def post(self, request, *args, **kwargs):
        user_ids = request.data.get('user_ids', [])
        if (user_ids == []):
            return Response({'detail': 'key "user_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in user_ids:
            try:
                User.objects.get(id = i)
            except:
                return Response({'detail': 'no find user has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        users_to_delete = User.objects.filter(id__in=user_ids)
        # lấy các account của users_to_delete
        accounts_to_delete = Account.objects.filter(id__in=users_to_delete.values('account'))
        # lấy các appointment của users_to_delete
        appointments_to_delete = Appointment.objects.filter(user__in=users_to_delete)

        print(users_to_delete)
        print(accounts_to_delete)
        print(appointments_to_delete)

        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        accounts_to_delete.delete()
        users_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)

@authentication_classes([])
class DeleteAdmins(GenericAPIView):
    def post(self, request, *args, **kwargs):
        admin_ids = request.data.get('admin_ids', [])
        if (admin_ids == []):
            return Response({'detail': 'key "admin_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in admin_ids:
            try:
                Admin.objects.get(id = i)
            except:
                return Response({'detail': 'no find admin has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        admins_to_delete = Admin.objects.filter(id__in=admin_ids)
        # lấy các account của admins_to_delete
        accounts_to_delete = Account.objects.filter(id__in=admins_to_delete.values('account'))
        # Thực hiện xoá đối tượng
        accounts_to_delete.delete()
        admins_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)

@authentication_classes([])
class DeleteHospitals(GenericAPIView):
    def post(self, request, *args, **kwargs):
        hospital_ids = request.data.get('hospital_ids', [])
        if (hospital_ids == []):
            return Response({'detail': 'key "hospital_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in hospital_ids:
            try:
                Hospital.objects.get(id = i)
            except:
                return Response({'detail': 'no find hospital has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        hospitals_to_delete = Hospital.objects.filter(id__in=hospital_ids)
        # lấy các account của hospitals_to_delete
        accounts_to_delete = Account.objects.filter(id__in=hospitals_to_delete.values('account'))
        # lấy các doctor của hospitals_to_delete
        doctors_to_delete = Doctor.objects.filter(hospital__in=hospitals_to_delete)
        # lấy các specialty_doctor của hospitals_to_delete
        specialty_doctors_to_delete = SpecialtyDoctor.objects.filter(doctor__in=doctors_to_delete)
        # lấy các service_doctor của hospitals_to_delete
        service_doctors_to_delete = ServiceDoctor.objects.filter(doctor__in=doctors_to_delete)
        # lấy các schedule của hospitals_to_delete
        schedules_to_delete = Schedule.objects.filter(schedule_doctor__doctor__in=doctors_to_delete)
        # lấy các schedule_doctor của hospitals_to_delete
        schedule_doctors_to_delete = Scheduler_Doctor.objects.filter(doctor__in=doctors_to_delete)
        # lấy các appointment của hospitals_to_delete
        appointments_to_delete = Appointment.objects.filter(schedule_doctor__doctor__in=doctors_to_delete)
        # lấy các blog của hospitals_to_delete
        blogs_to_delete = Blog.objects.filter(id_hospital__in=hospitals_to_delete)
        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        schedule_doctors_to_delete.delete()
        schedules_to_delete.delete()
        service_doctors_to_delete.delete()
        specialty_doctors_to_delete.delete()
        doctors_to_delete.delete()
        blogs_to_delete.delete()
        accounts_to_delete.delete()
        hospitals_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        doctor_ids = request.data.get('doctor_ids', [])
        if (doctor_ids == []):
            return Response({'detail': 'key "doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in doctor_ids:
            try:
                Doctor.objects.get(id = i)
            except:
                return Response({'detail': 'no find doctor has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        doctors_to_delete = Doctor.objects.filter(id__in=doctor_ids)
        # lấy các account của doctors_to_delete
        accounts_to_delete = Account.objects.filter(id__in=doctors_to_delete.values('account'))
        # lấy các specialty_doctor của doctors_to_delete
        specialty_doctors_to_delete = SpecialtyDoctor.objects.filter(doctor__in=doctors_to_delete)
        # lấy các service_doctor của doctors_to_delete
        service_doctors_to_delete = ServiceDoctor.objects.filter(doctor__in=doctors_to_delete)
        # lấy các schedule của doctors_to_delete
        schedules_to_delete = Schedule.objects.filter(schedule_doctor__doctor__in=doctors_to_delete)
        # lấy các schedule_doctor của doctors_to_delete
        schedule_doctors_to_delete = Scheduler_Doctor.objects.filter(doctor__in=doctors_to_delete)
        # lấy các appointment của doctors_to_delete
        appointments_to_delete = Appointment.objects.filter(schedule_doctor__doctor__in=doctors_to_delete)
        # lấy các blog của doctors_to_delete
        blogs_to_delete = Blog.objects.filter(id_doctor__in=doctors_to_delete)
        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        schedule_doctors_to_delete.delete()
        schedules_to_delete.delete()
        service_doctors_to_delete.delete()
        specialty_doctors_to_delete.delete()
        blogs_to_delete.delete()
        accounts_to_delete.delete()
        doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteSpecialties(GenericAPIView):
    def post(self, request, *args, **kwargs):
        specialty_ids = request.data.get('specialty_ids', [])
        if (specialty_ids == []):
            return Response({'detail': 'key "specialty_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in specialty_ids:
            try:
                Specialty.objects.get(id = i)
            except:
                return Response({'detail': 'no find specialty has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        specialties_to_delete = Specialty.objects.filter(id__in=specialty_ids)
        # lấy các specialty_doctor của specialties_to_delete
        specialty_doctors_to_delete = SpecialtyDoctor.objects.filter(specialty__in=specialties_to_delete)

        # Thực hiện xoá đối tượng
        specialty_doctors_to_delete.delete()
        specialties_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteSpecialtyDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        specialty_doctor_ids = request.data.get('specialty_doctor_ids', [])
        if (specialty_doctor_ids == []):
            return Response({'detail': 'key "specialty_doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in specialty_doctor_ids:
            try:
                SpecialtyDoctor.objects.get(id = i)
            except:
                return Response({'detail': 'no find specialty_doctor has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        specialty_doctors_to_delete = SpecialtyDoctor.objects.filter(id__in=specialty_doctor_ids)

        # Thực hiện xoá đối tượng
        specialty_doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteServices(GenericAPIView):
    def post(self, request, *args, **kwargs):
        service_ids = request.data.get('service_ids', [])
        if (service_ids == []):
            return Response({'detail': 'key "service_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in service_ids:
            try:
                Service.objects.get(id = i)
            except:
                return Response({'detail': 'no find service has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        services_to_delete = Service.objects.filter(id__in=service_ids)
        # lấy các service_doctor của services_to_delete
        service_doctors_to_delete = ServiceDoctor.objects.filter(service__in=services_to_delete)

        # Thực hiện xoá đối tượng
        service_doctors_to_delete.delete()
        services_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteServiceDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        service_doctor_ids = request.data.get('service_doctor_ids', [])
        if (service_doctor_ids == []):
            return Response({'detail': 'key "service_doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in service_doctor_ids:
            try:
                ServiceDoctor.objects.get(id = i)
            except:
                return Response({'detail': 'no find service_doctor has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        service_doctors_to_delete = ServiceDoctor.objects.filter(id__in=service_doctor_ids)
        
        # Thực hiện xoá đối tượng
        service_doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteSchedules(GenericAPIView):
    def post(self, request, *args, **kwargs):
        schedule_ids = request.data.get('schedule_ids', [])
        if (schedule_ids == []):
            return Response({'detail': 'key "schedule_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in schedule_ids:
            try:
                Schedule.objects.get(id = i)
            except:
                return Response({'detail': 'no find schedule has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        schedules_to_delete = Schedule.objects.filter(id__in=schedule_ids)
        # lấy các schedule_doctor của schedules_to_delete
        schedule_doctors_to_delete = Scheduler_Doctor.objects.filter(schedule__in=schedules_to_delete)
        # lấy các appointment của schedules_to_delete
        appointments_to_delete = Appointment.objects.filter(schedule_doctor__schedule__in=schedules_to_delete)

        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        schedule_doctors_to_delete.delete()
        schedules_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)

#create AddSchedulerDoctors
@authentication_classes([])
class AddSchedulerDoctors(GenericAPIView):
    serializer_class = SchedulerDoctorSerializer
    def post(self, request, *args, **kwargs):
        # data = request.data.copy()
        try: 
            request_data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return Response({'detail': 'Invalid JSON format in the request body'}, status=status.HTTP_400_BAD_REQUEST)
        # print(data)
        print(request_data)
        doctor_id = request_data.get('doctor_id', None)
        print('doctor_id: ', doctor_id)
        if doctor_id is None:
            return Response({'detail': 'key "doctor_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        
        schedule_ids = request_data.get('schedule_ids', [])
        print('schedule_ids: ', schedule_ids)
        if schedule_ids == []:
            return Response({'detail': 'key "schedule_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            doctor = Doctor.objects.get(id = doctor_id)
        except:
            return Response({'detail': 'no find doctor has id = '+str(doctor_id)}, status=status.HTTP_400_BAD_REQUEST)
        
        data_schedule_doctor = []
        schedule_doctors = []

        for i in schedule_ids:
            try:
                schedule = Schedule.objects.get(id = i)
            except:
                return Response({'detail': 'no find schedule has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
            if (Scheduler_Doctor.objects.filter(doctor=doctor, schedule=schedule).exists()):
                return Response({'detail': 'schedule_doctor: schedule_id = ' + str(i) + ' doctor_id = '+ str(doctor_id) + ' is exist'}, status=status.HTTP_400_BAD_REQUEST)
            data_schedule_doctor.append({'doctor': doctor, 'schedule': schedule})

        for i in data_schedule_doctor:
            schedule_doctor = Scheduler_Doctor.objects.create(doctor=i['doctor'], schedule=i['schedule'])
            schedule_doctors.append(schedule_doctor)    
        schedule_doctor.save()    

        serializer = SchedulerDoctorSerializer(schedule_doctors, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@authentication_classes([])
class DeleteSchedulerDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        scheduler_doctor_ids = request.data.get('scheduler_doctor_ids', [])
        if (scheduler_doctor_ids == []):
            return Response({'detail': 'key "scheduler_doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in scheduler_doctor_ids:
            try:
                Scheduler_Doctor.objects.get(id = i)
            except:
                return Response({'detail': 'no find scheduler_doctor has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        scheduler_doctors_to_delete = Scheduler_Doctor.objects.filter(id__in=scheduler_doctor_ids)
        # lấy các appointment của scheduler_doctors_to_delete
        appointments_to_delete = Appointment.objects.filter(schedule_doctor__in=scheduler_doctors_to_delete)
        
        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        scheduler_doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT) 
    
@authentication_classes([])
class DeleteAppointments(GenericAPIView):
    def post(self, request, *args, **kwargs):
        appointment_ids = request.data.get('appointment_ids', [])
        if (appointment_ids == []):
            return Response({'detail': 'key "appointment_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in appointment_ids:
            try:
                Appointment.objects.get(id = i)
            except:
                return Response({'detail': 'no find appointment has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        appointments_to_delete = Appointment.objects.filter(id__in=appointment_ids)
        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteTools(GenericAPIView):
    def post(self, request, *args, **kwargs):
        tool_ids = request.data.get('tool_ids', [])
        if (tool_ids == []):
            return Response({'detail': 'key "tool_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in tool_ids:
            try:
                Tool.objects.get(id = i)
            except:
                return Response({'detail': 'no find tool has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        tools_to_delete = Tool.objects.filter(id__in=tool_ids)
        # Thực hiện xoá đối tượng
        tools_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteCategories(GenericAPIView):
    def post(self, request, *args, **kwargs):
        category_ids = request.data.get('category_ids', [])
        if (category_ids == []):
            return Response({'detail': 'key "category_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in category_ids:
            try:
                Category.objects.get(id = i)
            except:
                return Response({'detail': 'no find category has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        categories_to_delete = Category.objects.filter(id__in=category_ids)
        # Thực hiện xoá đối tượng
        categories_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
    
@authentication_classes([])
class DeleteBlogs(GenericAPIView):
    def post(self, request, *args, **kwargs):
        blog_ids = request.data.get('blog_ids', [])
        if (blog_ids == []):
            return Response({'detail': 'key "blog_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in blog_ids:
            try:
                Blog.objects.get(id = i)
            except:
                return Response({'detail': 'no find blog has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        blogs_to_delete = Blog.objects.filter(id__in=blog_ids)
        # Thực hiện xoá đối tượng
        blogs_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)