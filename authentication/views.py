from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from hibacsi import settings
from django.contrib import auth
import jwt
from app.serializers import AccountSerializer, UserSerializer
from app.models import Account
from app.permissions import IsAdminPermission
import app.utils as utils
from rest_framework.decorators import authentication_classes, permission_classes
from datetime import datetime, timedelta

# Create your views here.
class LoginView(GenericAPIView):
    serializer_class = AccountSerializer
    def post(self, request):
        data = request.data
        username = data.get('username', '')
        password = data.get('password', '')
        isSuccess = utils.login_success(username=username, password=password)
        if isSuccess:
            account = Account.objects.get(username=username)
            auth_token = jwt.encode({   
                    "username": account.username, 
                    "type": "short",
                    "exp": datetime.utcnow() + timedelta(minutes=2) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
            payload = jwt.decode(auth_token, settings.JWT_SECRET_KEY, algorithms='HS256')
            print("payload", payload)
            serializer = AccountSerializer(account)
            data = {'user': serializer.data, 'token': auth_token}
            return Response(data, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class RegisterView(GenericAPIView):
    serializer_class = AccountSerializer
    def post(self, request):
        data = request.data.copy()
        data['role'] = 'user'
        data['password'] = utils.hash_password(data['password'])
        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            account = serializer.save()
            auth_token = jwt.encode(
                {'username': account.username ,
                 "exp": datetime.utcnow() + timedelta(minutes=2) }, settings.JWT_SECRET_KEY, algorithm='HS256')
            data = {'account': serializer.data, 'token': auth_token}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAdminPermission])
class RegisterViewAdmin(GenericAPIView):
    serializer_class = AccountSerializer
    def post(self, request):
        data = request.data.copy()
        data['role'] = 'admin'
        data['password'] = utils.hash_password(data['password'])
        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            account = serializer.save()
            auth_token = jwt.encode(
                {'username': account.username, 
                 "exp": datetime.utcnow() + timedelta(minutes=2) }, settings.JWT_SECRET_KEY, algorithm='HS256')
            data = {'account': serializer.data, 'token': auth_token}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
