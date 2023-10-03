from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'passwod', 'email')

import hashlib
def hash_password(password):
    salt = "random string to make the hash more secure"
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'password', 'email']

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if Account.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists.')
        if Account.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists.')
        data['role'] = 'user'
        data['password'] = hash_password(data['password'])
        return data
    
