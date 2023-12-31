import os
import json
import datetime
import app.utils as utils
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action, authentication_classes, permission_classes
from .serializers import *
from .models import Account
# from authentication.backends import JWTAuthentication
# from hibacsi.pagination import CustomLimitOffsetPagination
from app.permissions import IsAdminPermission, IsDoctorPermission, IsHospitalPermission, IsUserPermission
# JWTAuthentication
from authentication.backends import JWTAuthentication
from urllib.parse import urljoin




# các hàm hỗ trợ
def print_log(message):
    log_file_path = os.path.join(settings.BASE_DIR, 'log.txt')
    with open(log_file_path, 'a') as log_file:
        log_file.write(str(datetime.datetime.now()) + '\n' + message + '\n\n')
    pass

# account
@authentication_classes([])
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    # read all
    def list(self, request, *args, **kwargs):
        print("list account")
        JWTAuthentication.authenticate(self, request)
        # check permission
        if (IsAdminPermission.has_permission(self, request, self)):
            return super().list(request, *args, **kwargs)
        return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
    # update
    def update(self, request, *args, **kwargs):
        print("update account")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and User has id = kwargs['pk'], Doctor has id = kwargs['pk'], Hospital has id = kwargs['pk']
        if (str(request.account.id) != str(kwargs['pk'])):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    

    def partial_update(self, request, *args, **kwargs):
        print("partial_update account")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and User has id = kwargs['pk'], Doctor has id = kwargs['pk'], Hospital has id = kwargs['pk']
        if (str(request.account.id) != str(kwargs['pk'])):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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


# user
@authentication_classes([])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create user")
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list user")
        return super().list(request, *args, **kwargs)

    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve user")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update user")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and User has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsUserPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsUserPermission.has_permission(self, request, self)):
            try:
                user = User.objects.get(account=request.account)
            except:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(user.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update user")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and User has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsUserPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsUserPermission.has_permission(self, request, self)):
            try:
                user = User.objects.get(account=request.account)
            except:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(user.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        print("get_queryset user")
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
        print("destroy user")
        JWTAuthentication.authenticate(self, request)
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsUserPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsUserPermission.has_permission(self, request, self)):
            try:
                user = User.objects.get(account=request.account)
            except:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(user.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # lấy user
        user = self.get_object()
        # lấy account
        account = Account.objects.get(id=user.account.id)
        # lấy appointment 
        appointments = Appointment.objects.filter(user=user)
        # thực hiện xoá
        appointments.delete()
        account.delete()
        return Response({'detail': 'Delete success'}, status=status.HTTP_200_OK)

# delete some users
@permission_classes([IsAdminPermission])
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

# admin
@authentication_classes([]) 
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create admin")
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # read all
    def list(self, request, *args, **kwargs):
        print("list admin")
        JWTAuthentication.authenticate(self, request)
        # check permission
        if (not IsAdminPermission.has_permission(self, request, self)): 
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve admin")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update admin")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                admin = Admin.objects.get(account=request.account)
            except:
                return Response({'detail': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(admin.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update admin")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                admin = Admin.objects.get(account=request.account)
            except:
                return Response({'detail': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(admin.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        print("destroy admin")
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# delete some admins
@authentication_classes([])
class DeleteAdmins(GenericAPIView):
    def post(self, request, *args, **kwargs):
        # not allow
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # admin_ids = request.data.get('admin_ids', [])
        # if (admin_ids == []):
        #     return Response({'detail': 'key "admin_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # # Xác định các đối tượng cần xoá
        # for i in admin_ids:
        #     try:
        #         Admin.objects.get(id = i)
        #     except:
        #         return Response({'detail': 'no find admin has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        # admins_to_delete = Admin.objects.filter(id__in=admin_ids)
        # # lấy các account của admins_to_delete
        # accounts_to_delete = Account.objects.filter(id__in=admins_to_delete.values('account'))
        # # Thực hiện xoá đối tượng
        # accounts_to_delete.delete()
        # admins_to_delete.delete()
        # return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)

# blogCRUD
@authentication_classes([])
class BlogCRUDViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogCRUDSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create blog")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and Doctor
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
     
    # update
    def update(self, request, *args, **kwargs):
        print("update blog")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsDoctorPermission.has_permission(self, request, self)):
            try:
                doctor = Doctor.objects.get(account=request.account)
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            # check doctor is author of blog 
            try:
                blog = Blog.objects.get(id=kwargs['pk'])
            except:
                return Response({'detail': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(blog.id_doctor.id) != str(doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update blog")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsDoctorPermission.has_permission(self, request, self)):
            try:
                doctor = Doctor.objects.get(account=request.account)
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            # check doctor is author of blog 
            try:
                blog = Blog.objects.get(id=kwargs['pk'])
            except:
                return Response({'detail': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(blog.id_doctor.id) != str(doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

@authentication_classes([])
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def retrieve(self, request, *args, **kwargs):
        # Lấy đối tượng blog
        blog = self.get_object()
        # Tăng số lượt xem của blog lên 1
        blog.view += 1
        blog.save()
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params

        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}

        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model Blog nếu không thì báo lỗi
            if param in [field.name for field in Blog._meta.get_fields()]:
                filter_kwargs[param] = value
        
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)

        return queryset

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


# category
@authentication_classes([])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        print("create category")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        try: 
            name = data['name']
        except KeyError:
            return Response({'detail': 'key "name" is require'}, status=status.HTTP_400_BAD_REQUEST)

        if (Category.objects.filter(name=name).exists()):
            return Response({'detail': 'category is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update category")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update category")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        print("destroy category")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

@permission_classes([IsAdminPermission])
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


# doctor 
@authentication_classes([])
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create doctor")
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list doctor")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve doctor")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin, Hospital of Doctor and Doctor has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            # check doctor is in hospital
            try:
                doctor = Doctor.objects.get(id=kwargs['pk'])
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(doctor.hospital.id) != str(hospital.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsDoctorPermission.has_permission(self, request, self)):
            try:
                doctor = Doctor.objects.get(account=request.account)
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(doctor.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin, Hospital of Doctor and Doctor has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            # check doctor is in hospital
            try:
                doctor = Doctor.objects.get(id=kwargs['pk'])
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(doctor.hospital.id) != str(hospital.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsDoctorPermission.has_permission(self, request, self)):
            try:
                doctor = Doctor.objects.get(account=request.account)
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(doctor.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

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
        print("destroy doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin, Hospital of Doctor and Doctor has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            # check doctor is in hospital
            try:
                doctor = Doctor.objects.get(id=kwargs['pk'])
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(doctor.hospital.id) != str(hospital.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsDoctorPermission.has_permission(self, request, self)):
            try:
                doctor = Doctor.objects.get(account=request.account)
            except:
                return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(doctor.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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
    
# delete some doctors
class DeleteDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some doctors")
        # lấy doctor_ids
        doctor_ids = request.data.get('doctor_ids', [])
        if (doctor_ids == []):
            return Response({'detail': 'key "doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # check permission Admin, Hospital of Doctor
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            # check doctor is in hospital
            for i in doctor_ids:
                try:
                    doctor = Doctor.objects.get(id=i)
                except:
                    return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
                if (str(doctor.hospital.id) != str(hospital.id)):
                    return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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


# hospital
@authentication_classes([]) 
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create hospital")
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list hospital")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve hospital")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update hospital")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and Hospital has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(hospital.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update hospital")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and Hospital has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(hospital.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    # def read(self, request, *args, **kwargs):
    #     hospital = Hospital.objects.get(id = kwargs['pk'])
    #     # serializer = HospitalSerializer(hospital)
    #     content = {
    #         **HospitalSerializer(hospital).data,
    #         'account': AccountSerializer(hospital.account).data
    #     }
    #     return Response(content, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        print("destroy hospital")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin and Hospital has id = kwargs['pk']
        if ((not IsAdminPermission.has_permission(self, request, self)) and (not IsHospitalPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsHospitalPermission.has_permission(self, request, self)):
            try:
                hospital = Hospital.objects.get(account=request.account)
            except:
                return Response({'detail': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
            if (str(hospital.id) != str(kwargs['pk'])):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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

# delete some hospitals 
class DeleteHospitals(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some hospitals")
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        # lấy hospital_ids
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

# specialty
@authentication_classes([])
class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

    def create(self, request, *args, **kwargs):
        print("create specialty")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        if (Specialty.objects.filter(name=data['name']).exists()):
            return Response({'detail': 'specialty is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list specialty")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve specialty")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update specialty")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update specialty")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        print("destroy specialty")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        # lấy specialty
        specialty = self.get_object()
        # lấy specialtydoctor
        specialtydoctors = SpecialtyDoctor.objects.filter(specialty=specialty)
        print(specialtydoctors)
        # thực hiện xoá
        specialtydoctors.delete()
        return super().destroy(request, *args, **kwargs)
    
# delete some specialties
class DeleteSpecialties(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some specialties")
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create service")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        if (Service.objects.filter(name=data['name']).exists()):
            return Response({'detail': 'service is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list service")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve service")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update service")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update service")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        print("destroy service")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        # lấy service
        service = self.get_object()
        # lấy servicedoctor
        servicedoctors = ServiceDoctor.objects.filter(service=service)
        print(servicedoctors)
        # thực hiện xoá
        servicedoctors.delete()
        return super().destroy(request, *args, **kwargs)
    
# delete some services
class DeleteServices(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some services")
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        print("create schedule")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        days_of_week = data['days_of_week']
        time_start = data['start']
        time_end = data['end']
        if (Schedule.objects.filter(days_of_week=days_of_week, start=time_start, end=time_end).exists()):
            return Response({'detail': 'schedule is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    # read all
    def list(self, request, *args, **kwargs):
        print("list schedule")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve schedule")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update schedule")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update schedule")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        print("destroy schedule")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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
    
# delete some schedules
@authentication_classes([])
class DeleteSchedules(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some schedules")
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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

# schedule_doctor  # notenote
@authentication_classes([])
class SchedulerDoctorViewSet(viewsets.ModelViewSet):
    queryset = Scheduler_Doctor.objects.all()
    serializer_class = SchedulerDoctorSerializer
    # create
    def create(self, request, *args, **kwargs):
        print("create schedule_doctor")
        JWTAuthentication.authenticate(self, request)
        data = request.data.copy()
        print(data['doctor_id'])
        try:
            data['id_doctor'] = Doctor.objects.get(id = data['doctor_id'])
            data['id_schedule'] = Schedule.objects.get(id = data['schedule_id'])
        except:
            return Response({'detail': 'no find doctor or schedule'}, status=status.HTTP_400_BAD_REQUEST)
        # check permission Doctor has id = doctor_id
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else: 
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # check doctor is schedule_doctor
            if (str(doctor.id) != str(data['id_doctor'].id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if (Scheduler_Doctor.objects.filter(doctor=data['id_doctor'], schedule=data['id_schedule']).exists()):
            return Response({'detail': 'schedule_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        schedule_doctor = Scheduler_Doctor.objects.create(doctor=data['id_doctor'], schedule=data['id_schedule'])
        schedule_doctor.save()
        serializer = SchedulerDoctorSerializer(schedule_doctor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list schedule_doctor")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve schedule_doctor")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update schedule_doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Doctor of schedule_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy schedule_doctor
            schedule_doctor = self.get_object()
            # check doctor is schedule_doctor
            if (str(doctor.id) != str(schedule_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        try:
            data['id_doctor'] = Doctor.objects.get(id = data['doctor_id'])
            data['id_schedule'] = Schedule.objects.get(id = data['schedule_id'])
        except:
            return Response({'detail': 'no find doctor or schedule'}, status=status.HTTP_400_BAD_REQUEST)
        if (Scheduler_Doctor.objects.filter(doctor=data['id_doctor'], schedule=data['id_schedule']).exists()):
            return Response({'detail': 'schedule_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update schedule_doctor")
        return super().partial_update(request, *args, **kwargs)
    
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
        print("destroy schedule_doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Doctor of schedule_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy schedule_doctor
            schedule_doctor = self.get_object()
            # check doctor is schedule_doctor
            if (str(doctor.id) != str(schedule_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        # lấy schedule_doctor
        schedule_doctor = self.get_object()
        # lấy appointment
        appointments = Appointment.objects.filter(schedule_doctor=schedule_doctor)
        print(schedule_doctor)
        print(appointments)
        # thực hiện xoá
        appointments.delete()
        return super().destroy(request, *args, **kwargs)
    
# delete some schedule_doctors
class DeleteSchedulerDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some schedule_doctors")
        scheduler_doctor_ids = request.data.get('scheduler_doctor_ids', [])
        if (scheduler_doctor_ids == []):
            return Response({'detail': 'key "scheduler_doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)        
        # Xác định các đối tượng cần xoá
        for i in scheduler_doctor_ids:
            try:
                Scheduler_Doctor.objects.get(id = i)
            except:
                return Response({'detail': 'no find scheduler_doctor has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        # check permission Doctor of list of schedule_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy schedule_doctor
            schedule_doctors = Scheduler_Doctor.objects.filter(id__in=scheduler_doctor_ids)
            # check doctor is schedule_doctor
            for i in schedule_doctors:
                if (str(doctor.id) != str(i.doctor.id)):
                    return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        scheduler_doctors_to_delete = Scheduler_Doctor.objects.filter(id__in=scheduler_doctor_ids)
        # lấy các appointment của scheduler_doctors_to_delete
        appointments_to_delete = Appointment.objects.filter(schedule_doctor__in=scheduler_doctors_to_delete)
        
        # Thực hiện xoá đối tượng
        appointments_to_delete.delete()
        scheduler_doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT) 

# add some schedule_doctors
class AddSchedulerDoctors(GenericAPIView):
    serializer_class = SchedulerDoctorSerializer
    def post(self, request, *args, **kwargs):
        print("add some schedule_doctors")
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
        # check permission Doctor has id = doctor_id
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else: 
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # check doctor is schedule_doctor
            if (str(doctor.id) != str(doctor_id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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


# appointment
@authentication_classes([])
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create appointment")
        return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # read all
    def list(self, request, *args, **kwargs):
        print("list appointment")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve appointment")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update appointment")
        JWTAuthentication.authenticate(self, request)
        # check permission User or Doctor of appointment
        if ((not IsUserPermission.has_permission(self, request, self)) and (not IsDoctorPermission.has_permission(self, request, self))):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsUserPermission.has_permission(self, request, self)):
            # lấy user
            user = User.objects.get(account=request.account)
            # lấy appointment
            appointment = self.get_object()
            # check user is appointment
            if (str(user.id) != str(appointment.user.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif (IsDoctorPermission.has_permission(self, request, self)):
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy appointment
            appointment = self.get_object()
            # check doctor is appointment
            if (str(doctor.id) != str(appointment.schedule_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
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
    
    # destroy
    def destroy(self, request, *args, **kwargs):
        print("destroy appointment")
        JWTAuthentication.authenticate(self, request)
        # check permission Admin
        if (not IsAdminPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

# delete some appointments
@permission_classes([IsAdminPermission])
class DeleteAppointments(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some appointments")
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
            if i.status == 0:
                appointment_not_confirm.append(i)
            elif i.status == 1:
                if i.date < datetime.date.today() or (i.date == datetime.date.today() and i.schedule_doctor.schedule.end < datetime.datetime.now().time()):
                    appointment_confirmed.append(i)
                else:
                    appointment_coming.append(i)
            elif i.status == 2:
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

        serializer = GetAppointmentSerializer(data=serializer_data)
        serializer.is_valid()
        # add http for avatar
        base_url = r'http://' + request.get_host()
        for type_status in serializer.data:
            for i in range(len(serializer.data[type_status])):
                if str(serializer.data[type_status][i]['schedule_doctor']['doctor']['account']['avatar']) != '':
                    serializer.data[type_status][i]['schedule_doctor']['doctor']['account']['avatar'] = urljoin(base_url, serializer.data[type_status][i]['schedule_doctor']['doctor']['account']['avatar'])
                if str(serializer.data[type_status][i]['user']['account']['avatar']) != '':
                    serializer.data[type_status][i]['user']['account']['avatar'] = urljoin(base_url, serializer.data[type_status][i]['user']['account']['avatar'])
                if str(serializer.data[type_status][i]['schedule_doctor']['doctor']['hospital']['account']['avatar']) != '':
                    serializer.data[type_status][i]['schedule_doctor']['doctor']['hospital']['account']['avatar'] = urljoin(base_url, serializer.data[type_status][i]['schedule_doctor']['doctor']['hospital']['account']['avatar'])
        print(serializer.data['not_confirm'][0]['user']['account']['avatar'])
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
            try:
                appointment = Appointment.objects.get(id=kwargs['pk'])
            except Appointment.DoesNotExist:
                return Response({'detail': 'appointment is not exist'}, status=status.HTTP_400_BAD_REQUEST)
            if (doctor != appointment.schedule_doctor.doctor):
                return Response({'detail': 'doctor is not doctor of appointment'}, status=status.HTTP_400_BAD_REQUEST)
        except Doctor.DoesNotExist:
            user = User.objects.get(account=request.account)
            try:
                appointment = Appointment.objects.get(id=kwargs['pk'])
            except Appointment.DoesNotExist:
                return Response({'detail': 'appointment is not exist'}, status=status.HTTP_400_BAD_REQUEST)
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

# service doctor
@authentication_classes([])
class ServiceDoctorViewSet(viewsets.ModelViewSet):
    queryset = ServiceDoctor.objects.all()
    serializer_class = ServiceDoctorSerializer

    # create
    def create(self, request, *args, **kwargs):
        print("create service_doctor")
        JWTAuthentication.authenticate(self, request)
        data = request.data.copy()
        try:
            service_id = data['service_id']
        except KeyError:
            return Response({'detail': 'key "service_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor_id = data['doctor_id']
        except KeyError:
            return Response({'detail': 'key "doctor_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # check permission Doctor has id = doctor_id
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else: 
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # check doctor is service_doctor
            if (str(doctor.id) != str(doctor_id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            data['service'] = Service.objects.get(id = service_id)
        except:
            return Response({'detail': 'no find service has id = ' + str(service_id)}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data['doctor'] = Doctor.objects.get(id = doctor_id)
        except:
            return Response({'detail': 'no find doctor has id = ' + str(doctor_id)}, status=status.HTTP_400_BAD_REQUEST)
        if (ServiceDoctor.objects.filter(service=data['service'], doctor=data['doctor']).exists()):
            return Response({'detail': 'service_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        service_doctor = ServiceDoctor.objects.create(service=data['service'], doctor=data['doctor'])
        service_doctor.save()
        serializer = ServiceDoctorSerializer(service_doctor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # read all
    def list(self, request, *args, **kwargs):
        print("list service_doctor")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve service_doctor")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update service_doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Doctor of service_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy service_doctor
            service_doctor = self.get_object()
            # check doctor is service_doctor
            if (str(doctor.id) != str(service_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        try:
            service_id = data['service_id']
        except KeyError:
            return Response({'detail': 'key "service_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor_id = data['doctor_id']
        except KeyError:
            return Response({'detail': 'key "doctor_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data['service'] = Service.objects.get(id = service_id)
        except:
            return Response({'detail': 'no find service has id = ' + str(service_id)}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data['doctor'] = Doctor.objects.get(id = doctor_id)
        except:
            return Response({'detail': 'no find doctor has id = ' + str(doctor_id)}, status=status.HTTP_400_BAD_REQUEST)
        if (ServiceDoctor.objects.filter(service=data['service'], doctor=data['doctor']).exists()):
            return Response({'detail': 'service_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update service_doctor")
        return super().partial_update(request, *args, **kwargs)
    
    # destroy
    def destroy(self, request, *args, **kwargs):
        print("destroy service_doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Doctor of service_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy service_doctor
            service_doctor = self.get_object()
            # check doctor is service_doctor
            if (str(doctor.id) != str(service_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        # Tạo một từ điển kwargs để xây dựng truy vấn động
        filter_kwargs = {}
        # Lặp qua tất cả các tham số truy vấn và thêm chúng vào từ điển kwargs
        for param, value in params.items():
            # Đảm bảo rằng param tồn tại trong model ServiceDoctor nếu không thì báo lỗi
            if param in [field.name for field in ServiceDoctor._meta.get_fields()]:
                filter_kwargs[param] = value
        # Xây dựng truy vấn động bằng cách sử dụng **kwargs
        queryset = queryset.filter(**filter_kwargs)

        return queryset

# delete some service_doctors
class DeleteServiceDoctors(GenericAPIView):
    def post(self, request, *args, **kwargs):
        print("delete some service_doctors")
        service_doctor_ids = request.data.get('service_doctor_ids', [])
        if (service_doctor_ids == []):
            return Response({'detail': 'key "service_doctor_ids" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # Xác định các đối tượng cần xoá
        for i in service_doctor_ids:
            try:
                ServiceDoctor.objects.get(id = i)
            except:
                return Response({'detail': 'no find service_doctor has id = '+str(i)}, status=status.HTTP_400_BAD_REQUEST)
        # check permission Doctor of list of service_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy service_doctor
            service_doctors = ServiceDoctor.objects.filter(id__in=service_doctor_ids)
            # check doctor is service_doctor
            for i in service_doctors:
                if (str(doctor.id) != str(i.doctor.id)):
                    return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        service_doctors_to_delete = ServiceDoctor.objects.filter(id__in=service_doctor_ids)
        
        # Thực hiện xoá đối tượng
        service_doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)


# specialty doctor
@authentication_classes([])
class SpecialtyDoctorViewSet(viewsets.ModelViewSet):
    queryset = SpecialtyDoctor.objects.all()
    serializer_class = SpecialtyDoctorSerializer
    # create
    def create(self, request, *args, **kwargs):
        print("create specialty_doctor")
        JWTAuthentication.authenticate(self, request)
        data = request.data.copy()
        try:
            specialty_id = data['specialty_id']
        except KeyError:
            return Response({'detail': 'key "specialty_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor_id = data['doctor_id']
        except KeyError:
            return Response({'detail': 'key "doctor_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        # check permission Doctor has id = doctor_id
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # check doctor is specialty_doctor
            if (str(doctor.id) != str(doctor_id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            data['specialty'] = Specialty.objects.get(id = specialty_id)
        except:
            return Response({'detail': 'no find specialty has id = ' + str(specialty_id)}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            data['doctor'] = Doctor.objects.get(id = doctor_id)
        except:
            return Response({'detail': 'no find doctor has id = ' + str(doctor_id)}, status=status.HTTP_400_BAD_REQUEST)
        if (SpecialtyDoctor.objects.filter(specialty=data['specialty'], doctor=data['doctor']).exists()):
            return Response({'detail': 'specialty_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        specialty_doctor = SpecialtyDoctor.objects.create(specialty=data['specialty'], doctor=data['doctor'])
        specialty_doctor.save()
        serializer = SpecialtyDoctorSerializer(specialty_doctor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # read all
    def list(self, request, *args, **kwargs):
        print("list specialty_doctor")
        return super().list(request, *args, **kwargs)
    
    # retrieve
    def retrieve(self, request, *args, **kwargs):
        print("retrieve specialty_doctor")
        return super().retrieve(request, *args, **kwargs)
    
    # update
    def update(self, request, *args, **kwargs):
        print("update specialty_doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Doctor of specialty_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy specialty_doctor
            specialty_doctor = self.get_object()
            # check doctor is specialty_doctor
            if (str(doctor.id) != str(specialty_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        try:
            specialty_id = data['specialty_id']
        except KeyError:
            return Response({'detail': 'key "specialty_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor_id = data['doctor_id']
        except KeyError:
            return Response({'detail': 'key "doctor_id" is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data['specialty'] = Specialty.objects.get(id = specialty_id)
        except:
            return Response({'detail': 'no find specialty has id = ' + str(specialty_id)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data['doctor'] = Doctor.objects.get(id = doctor_id)
        except:
            return Response({'detail': 'no find doctor has id = ' + str(doctor_id)}, status=status.HTTP_400_BAD_REQUEST)
        if (SpecialtyDoctor.objects.filter(specialty=data['specialty'], doctor=data['doctor']).exists()):
            return Response({'detail': 'specialty_doctor is exist'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
    
    # partial_update
    def partial_update(self, request, *args, **kwargs):
        print("partial_update specialty_doctor")
        return super().partial_update(request, *args, **kwargs)
    
    # destroy
    def destroy(self, request, *args, **kwargs):
        print("destroy specialty_doctor")
        JWTAuthentication.authenticate(self, request)
        # check permission Doctor of specialty_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy specialty_doctor
            specialty_doctor = self.get_object()
            # check doctor is specialty_doctor
            if (str(doctor.id) != str(specialty_doctor.doctor.id)):
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

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
    
# delete some specialty_doctors
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
        # check permission Doctor of list of specialty_doctor
        if (not IsDoctorPermission.has_permission(self, request, self)):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # lấy doctor
            doctor = Doctor.objects.get(account=request.account)
            # lấy specialty_doctor
            specialty_doctors = SpecialtyDoctor.objects.filter(id__in=specialty_doctor_ids)
            # check doctor is specialty_doctor
            for i in specialty_doctors:
                if (str(doctor.id) != str(i.doctor.id)):
                    return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)    
        
        specialty_doctors_to_delete = SpecialtyDoctor.objects.filter(id__in=specialty_doctor_ids)

        # Thực hiện xoá đối tượng
        specialty_doctors_to_delete.delete()
        return Response({'message': 'Xoá thành công'}, status=status.HTTP_204_NO_CONTENT)

# tool
@authentication_classes([])
class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer

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
        
# statisticalAppointmentAPIView
@authentication_classes([])
class statisticalAppointmentAPIView(GenericAPIView):
    def get(self, request):
        # get scope param
        try:
            scope = request.query_params['scope']
            print('scope: ', scope)  #week, month, year, all
        except KeyError:
            return Response({'detail': 'key "scope" is require'}, status=status.HTTP_400_BAD_REQUEST)
        if scope not in ['week', 'month', 'year', 'all']:
            return Response({'detail': 'scope must be week, month, year, all'}, status=status.HTTP_400_BAD_REQUEST)
        # get appointment
        if scope == 'all':
            appointment = Appointment.objects.all()
        elif scope == 'week':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
        elif scope == 'month':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        elif scope == 'year':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()])
        print(len(appointment))
        # total appointment (status = 1)
        appointment_confirmed = appointment.filter(status=1)
        total_appointment = len(appointment_confirmed)
        # revenue = sum(doctor.price) for doctor in appointment
        revenue = sum([appointment.schedule_doctor.doctor.price for appointment in appointment_confirmed])
        print('total_appointment: ', total_appointment)
        print('revenue: ', revenue)
        # not_confirm 
        appointment_not_confirm = appointment.filter(status=0)
        num_appointment_not_confirm = len(appointment_not_confirm)
        # cancel
        appointment_cancel = appointment.filter(status=2)
        num_appointment_cancel = len(appointment_cancel)

        # bieu do thong ke doanh thu theo thoi gian
        # cot x: thoi gian
        time_row = []
        if scope == 'all':
            # get year start and end
            start = appointment_confirmed.first().date.year
            end = appointment_confirmed.last().date.year
        elif scope == 'year': # 12 thang
            start = datetime.date.today() - datetime.timedelta(days=365)
            end = datetime.date.today()
        elif scope == 'month': # 30 ngay
            start = datetime.date.today() - datetime.timedelta(days=30)
            end = datetime.date.today()
        elif scope == 'week': # 7 ngay
            start = datetime.date.today() - datetime.timedelta(days=7)
            end = datetime.date.today()
        
        if scope == 'all': 
            for i in range(start, end+1):
                time_row.append(i)
        elif scope == 'year':
            current_date = datetime.date(start.year, start.month, 1)
            while current_date <= end:
                time_row.append(current_date.strftime('%Y-%m'))
                # Tăng thêm 1 tháng
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        else:
            current_date = start

            while current_date <= end:
                time_row.append(current_date.strftime('%Y-%m-%d'))
                current_date += datetime.timedelta(days=1)

        print(time_row) 

        # cot y: doanh thu
        revenue_col = []
        if scope == 'all':
            for i in range(start, end+1):
                revenue_col.append(sum([appointment.schedule_doctor.doctor.price for appointment in appointment_confirmed if appointment.date.year == i]))
        elif scope == 'year':
            current_date = datetime.date(start.year, start.month, 1)
            while current_date <= end:
                revenue_col.append(sum([appointment.schedule_doctor.doctor.price for appointment in appointment_confirmed if appointment.date.strftime('%Y-%m') == current_date.strftime('%Y-%m')]))
                # Tăng thêm 1 tháng
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        else:
            current_date = start

            while current_date <= end:
                revenue_col.append(sum([appointment.schedule_doctor.doctor.price for appointment in appointment_confirmed if appointment.date.strftime('%Y-%m-%d') == current_date.strftime('%Y-%m-%d')]))
                current_date += datetime.timedelta(days=1)

        print(revenue_col)

        return Response({
            'total_appointment': total_appointment,
            'revenue': revenue,
            'num_appointment_not_confirm': num_appointment_not_confirm,
            'num_appointment_cancel': num_appointment_cancel,
            'time_row': time_row,
            'revenue_col': revenue_col
        }, status=status.HTTP_200_OK)
    

# statisticalTopDoctorAPIView
@authentication_classes([])
class statisticalTopDoctorAPIView(GenericAPIView): 
    serializer_class = DoctorStatisticalSerializer
    def get(self, request):
        # get scope param
        try:
            scope = request.query_params['scope']
            print('scope: ', scope)  #week, month, year, all
        except KeyError:
            return Response({'detail': 'key "scope" is require'}, status=status.HTTP_400_BAD_REQUEST)
        if scope not in ['week', 'month', 'year', 'all']:
            return Response({'detail': 'scope must be week, month, year, all'}, status=status.HTTP_400_BAD_REQUEST)
        # get appointment
        if scope == 'all':
            appointment = Appointment.objects.all()
        elif scope == 'week':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
        elif scope == 'month':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        elif scope == 'year':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()])
        appointment_confirmed = appointment.filter(status=1)
        # top doctor in appointment in scope
        doctors = [appointment.schedule_doctor.doctor for appointment in appointment_confirmed]
        # Sử dụng từ điển để đếm số lần xuất hiện của mỗi doctor_id
        doctor_counts = {}
        for doctor in doctors:
            if doctor in doctor_counts:
                doctor_counts[doctor] += 1
            else:
                doctor_counts[doctor] = 1
        # Sắp xếp theo số lần xuất hiện giảm dần
        sorted_doctor_counts = sorted(doctor_counts.items(), key=lambda x: x[1], reverse=True)
        print(sorted_doctor_counts)
        # change sorted_doctor_counts to {"doctor": doctor, "count": count}
        sorted_doctor_counts = [{"doctor": i[0], "count": i[1]} for i in sorted_doctor_counts]
        serializers = DoctorStatisticalSerializer(sorted_doctor_counts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)    
    
# statisticalTopUserAPIView
@authentication_classes([])
class statisticalTopUserAPIView(GenericAPIView): 
    serializer_class = UserStatisticalSerializer
    def get(self, request):
        # get scope param
        try:
            scope = request.query_params['scope']
            print('scope: ', scope)  #week, month, year, all
        except KeyError:
            return Response({'detail': 'key "scope" is require'}, status=status.HTTP_400_BAD_REQUEST)
        if scope not in ['week', 'month', 'year', 'all']:
            return Response({'detail': 'scope must be week, month, year, all'}, status=status.HTTP_400_BAD_REQUEST)
        # get appointment
        if scope == 'all':
            appointment = Appointment.objects.all()
        elif scope == 'week':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
        elif scope == 'month':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        elif scope == 'year':
            appointment = Appointment.objects.filter(date__range=[datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()])
        appointment_confirmed = appointment.filter(status=1)
        # top user in appointment in scope
        users = [appointment.user for appointment in appointment_confirmed]
        # Sử dụng từ điển để đếm số lần xuất hiện của mỗi user_id
        user_counts = {}
        for user in users:
            if user in user_counts:
                user_counts[user] += 1
            else:
                user_counts[user] = 1
        # Sắp xếp theo số lần xuất hiện giảm dần
        sorted_user_counts = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
        print(sorted_user_counts)
        # change sorted_user_counts to {"user": user, "count": count}
        sorted_user_counts = [{"user": i[0], "count": i[1]} for i in sorted_user_counts]
        serializers = UserStatisticalSerializer(sorted_user_counts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    

# statisticalBlogAPIView
@authentication_classes([])
class statisticalBlogAPIView(GenericAPIView):
    def get(self, request):
        # get scope param
        try:
            scope = request.query_params['scope']
            print('scope: ', scope)  #week, month, year, all
        except KeyError:
            return Response({'detail': 'key "scope" is require'}, status=status.HTTP_400_BAD_REQUEST)
        if scope not in ['week', 'month', 'year', 'all']:
            return Response({'detail': 'scope must be week, month, year, all'}, status=status.HTTP_400_BAD_REQUEST)
        # get blog
        if scope == 'all':
            blog = Blog.objects.all()
        elif scope == 'week':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
        elif scope == 'month':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        elif scope == 'year':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()])
        # total blog
        total_blog = len(blog)
        # tổng view 
        total_view = sum([i.view for i in blog])
        # bieu do thong ke so luong truy cap blog
        if scope in ['all', 'year']:
            limit = 20
        else:
            limit = 10
        # cot x: blog
        blog_row = [i.title for i in blog]
        # cot y: view
        view_col = [i.view for i in blog]
        # sap xep giam dan view_col ăn theo blog_row
        view_col, blog_row = zip(*sorted(zip(view_col, blog_row), reverse=True))
        # lay limit
        blog_row = blog_row[:limit]
        view_col = view_col[:limit]
        print(blog_row)
        print(view_col)
        return Response({
            'total_blog': total_blog,
            'total_view': total_view,
            'blog_row': blog_row,
            'view_col': view_col
        }, status=status.HTTP_200_OK)
    
# statisticalTopCategoryAPIView
@authentication_classes([])
class statisticalTopCategoryAPIView(GenericAPIView):
    serializer_class = CategoryStatisticalSerializer
    def get(self, request): 
        # get scope param
        try:
            scope = request.query_params['scope']
            print('scope: ', scope)  #week, month, year, all
        except KeyError:
            return Response({'detail': 'key "scope" is require'}, status=status.HTTP_400_BAD_REQUEST)
        if scope not in ['week', 'month', 'year', 'all']:
            return Response({'detail': 'scope must be week, month, year, all'}, status=status.HTTP_400_BAD_REQUEST)
        # get blog
        if scope == 'all':
            blog = Blog.objects.all()
        elif scope == 'week':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
        elif scope == 'month':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        elif scope == 'year':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()])
        # top category in blog in scope
        categories = [i.id_category for i in blog]
        # Sử dụng từ điển để đếm số lần xuất hiện của mỗi category_id
        category_counts = {}
        for category in categories:
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        # Sắp xếp theo số lần xuất hiện giảm dần
        sorted_category_counts = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        print(sorted_category_counts)
        # change sorted_category_counts to {"category": category, "count": count}
        sorted_category_counts = [{"category": i[0], "count": i[1]} for i in sorted_category_counts]
        serializers = CategoryStatisticalSerializer(sorted_category_counts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
# statisticalTopDoctorBlogAPIView
@authentication_classes([])
class statisticalTopDoctorBlogAPIView(GenericAPIView):
    serializer_class = DoctorStatisticalSerializer
    def get(self, request):
        # get scope param
        try:
            scope = request.query_params['scope']
            print('scope: ', scope)  #week, month, year, all
        except KeyError:
            return Response({'detail': 'key "scope" is require'}, status=status.HTTP_400_BAD_REQUEST)
        if scope not in ['week', 'month', 'year', 'all']:
            return Response({'detail': 'scope must be week, month, year, all'}, status=status.HTTP_400_BAD_REQUEST)
        # get blog
        if scope == 'all':
            blog = Blog.objects.all()
        elif scope == 'week':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
        elif scope == 'month':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        elif scope == 'year':
            blog = Blog.objects.filter(created_at__range=[datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()])
        # top doctor in blog in scope
        doctors = [i.id_doctor for i in blog]
        # Sử dụng từ điển để đếm số lần xuất hiện của mỗi doctor_id
        doctor_counts = {}
        for doctor in doctors:
            if doctor in doctor_counts:
                doctor_counts[doctor] += 1
            else:
                doctor_counts[doctor] = 1
        # Sắp xếp theo số lần xuất hiện giảm dần
        sorted_doctor_counts = sorted(doctor_counts.items(), key=lambda x: x[1], reverse=True)
        print(sorted_doctor_counts)
        # change sorted_doctor_counts to {"doctor": doctor, "count": count}
        sorted_doctor_counts = [{"doctor": i[0], "count": i[1]} for i in sorted_doctor_counts]
        serializers = DoctorStatisticalSerializer(sorted_doctor_counts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)