from app.models import Account
import hashlib
import jwt
from django.conf import settings

def hash_password(password):
    salt = "random string to make the hash more secure"
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password

def login_success(username, password):
    try:
        account = Account.objects.get(username=username)
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