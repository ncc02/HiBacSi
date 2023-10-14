import jwt
from rest_framework import authentication, exceptions
from hibacsi import settings
from app.models import User, Account

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)
        if not auth_data:
            return None
        prefix, token = auth_data.decode('utf-8').split(' ')
        try: 
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms='HS256')
            account = Account.objects.get(username=payload['username'])
            type = payload['type']
            print("account", account)
            request.account = account
            request.type = type
            request.token = token
            return None
        except jwt.DecodeError as identifier:
            raise exceptions.AuthenticationFailed('Your token is invalid abc, login')
        except jwt.ExpiredSignatureError as identifier:
            raise exceptions.AuthenticationFailed('Your token is expired abc, login')
        # return super().authenticate(request)