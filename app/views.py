from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import *
# from django.contrib.auth.hashers import make_password

from .models import Account  # Import mô hình Account của bạn

def login_success(username, password):
    try:
        account = Account.objects.get(username=username)
        if password == account.password:
            return True
        else:
            return False
    except Account.DoesNotExist:
        return False



class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        success = login_success(username=username, password=password)
 
        if success:
            # Đăng nhập thành công
            account = Account.objects.get(username=username)
            account_data = AccountSerializer(account).data
            response_data = {
                'state': True,
                'account': account_data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Đăng nhập thất bại
            response_data = {'state': False}
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
