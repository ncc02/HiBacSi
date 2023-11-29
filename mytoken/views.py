from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from app.models import Account, User, Admin, Doctor, Hospital
from app.serializers import TokenSerializer, AccountSerializer, UserSerializer, AdminSerializer, DoctorSerializer, HospitalSerializer 
import app.utils as utils

# Create your views here.
from rest_framework.decorators import authentication_classes, permission_classes

@authentication_classes([])
class TokenRefreshView(GenericAPIView):
    serializer_class = TokenSerializer
    def post(self, request):
        data = request.data
        refreshToken = data.get('refreshToken', '')
        if (refreshToken == ''):
            return Response({'detail': 'No refresh token found'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            account = Account.objects.get(refresh_token=refreshToken)
        except Account.DoesNotExist:
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_403_FORBIDDEN)
        access_token = utils.generateAccessToken(account)
        serializer = {'refresh_token': refreshToken, 'access_token': access_token}
        return Response(serializer, status=status.HTTP_200_OK)

# @authentication_classes([])
class TokenVerifyView(GenericAPIView):
    serializer_class = UserSerializer
    def post(self, request):
        account = request.account
        print(account)
        role = account.role
        if (role == 'user'): 
            try:
                user = User.objects.get(account=account)
                serializer = UserSerializer(user)
                print(user)
            except User.DoesNotExist:   
                return Response({'detail': 'Invalid user'}, status=status.HTTP_403_FORBIDDEN)
        elif (role == 'admin'):
            try:
                admin = Admin.objects.get(account=account)
                serializer = AdminSerializer(admin)
            except Admin.DoesNotExist:
                return Response({'detail': 'Invalid admin'}, status=status.HTTP_403_FORBIDDEN)
        elif (role == 'doctor'):
            try:
                doctor = Doctor.objects.get(account=account)
                serializer = DoctorSerializer(doctor)
            except Doctor.DoesNotExist:
                return Response({'detail': 'Invalid doctor'}, status=status.HTTP_403_FORBIDDEN)
        elif (role == 'hospital'):
            try:
                hospital = Hospital.objects.get(account=account)
                serializer = HospitalSerializer(hospital)
            except Hospital.DoesNotExist:
                return Response({'detail': 'Invalid hospital'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.data, status=status.HTTP_200_OK)