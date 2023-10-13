from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from hibacsi import settings
from django.contrib import auth
import jwt
from app.serializers import AccountSerializer, UserSerializer
from app.models import Account
import app.utils as utils


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
            auth_token = jwt.encode(
                { "username": account.username }, settings.JWT_SECRET_KEY)
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
                {'username': account.username}, settings.JWT_SECRET_KEY)
            data = {'acccount': serializer.data, 'token': auth_token}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class RegisterUser(APIView):
#     def post(self, request):
#         data=request.data.copy()
#         data['role'] = 'user'
#         data['password'] = hash_password(data['password'])
#         serializer = AccountSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'state': True, 'message': 'Registration successful.'})
#         else:
#             return Response({'state': False, 'message': serializer.errors})