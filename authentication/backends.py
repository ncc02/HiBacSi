import jwt
from rest_framework import authentication, exceptions
from hibacsi import settings
from app.models import User, Account

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        print('JWTAuthentication')
        auth_data = authentication.get_authorization_header(request)
        print('forbidden')
        if not auth_data:
            raise exceptions.AuthenticationFailed('No token found')
        prefix, access_token = auth_data.decode('utf-8').split(' ')
        print('forbidden')
        try: 
            payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms='HS256')
            account = Account.objects.get(username=payload['username'])
            request.account = account
            request.access_token = access_token
        except jwt.DecodeError as identifier:
            raise exceptions.AuthenticationFailed('Your token is invalid, login')
        except jwt.ExpiredSignatureError as identifier:
            raise exceptions.AuthenticationFailed('Your token is expired, login')
        return (account, None)
        # return super().authenticate(request)