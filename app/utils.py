from app.models import Account
import hashlib
import jwt
from django.conf import settings
from datetime import datetime, timedelta

def hash_password(password):
    salt = "random string to make the hash more secure"
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password

def login_success(username, password, email):
    if username == '' and email == '':
        return False
    if password == '':
        return False
    if username != '':
        try:
            account = Account.objects.get(username=username)
            if  hash_password(password) == account.password:
                return True
            else:
                return False
        except Account.DoesNotExist:
            return False
    if email != '':
        try:
            account = Account.objects.get(email=email)
            if  hash_password(password) == account.password:
                return True
            else:
                return False
        except Account.DoesNotExist:
            return False
    
def generate_access_token(account):
    payload = {
        'username': account.username,
        'role': account.role
    }
    print(payload)
    print(settings.JWT_SECRET_KEY)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')



def generateTokens(account):
    refresh_token = jwt.encode({   
                    "username": account.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=2) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    access_token = jwt.encode({   
                    "username": account.username, 
                    "exp": datetime.utcnow() + timedelta(days=7) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    return refresh_token, access_token 

def generateAccessToken(account):
    access_token = jwt.encode({   
                    "username": account.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=2) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    return access_token

def updateRefreshToken(username, refreshToken):
    account = Account.objects.get(username=username)
    account.refresh_token = refreshToken
    account.save()