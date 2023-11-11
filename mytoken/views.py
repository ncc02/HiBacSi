from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from app.models import Account
from app.serializers import TokenSerializer, AccountSerializer
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
