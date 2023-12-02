from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    # def validate(self, data):
    #     username = data.get('username')
    #     email = data.get('email')

    #     if Account.objects.filter(username=username).exists():
    #         raise serializers.ValidationError('Username already exists.')
    #     if Account.objects.filter(email=email).exists():
    #         raise serializers.ValidationError('Email already exists.')
        
    #     return data

class UserSerializer(serializers.ModelSerializer):
    # account = AccountSerializer()
    class Meta:
        model = User
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    # account = AccountSerializer()
    class Meta:
        model = Admin
        fields = '__all__'

class HospitalSerializer(serializers.ModelSerializer):
    # account = AccountSerializer()
    class Meta:
        model = Hospital
        fields = '__all__'

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'

class SpecialtyDoctorSerializer(serializers.ModelSerializer):
  specialty = SpecialtySerializer()
  class Meta:
    model = SpecialtyDoctor
    fields = '__all__' 

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ServiceDoctorSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    class Meta:
        model = ServiceDoctor
        fields = '__all__'
    
class DoctorSerializer(serializers.ModelSerializer):
    # account = AccountSerializer()
    hospital = HospitalSerializer()
    specialties = SpecialtyDoctorSerializer(many=True, source='specialtydoctor_set')
    services = ServiceDoctorSerializer(many=True, source='servicedoctor_set')
    class Meta:
        model = Doctor
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class ScheduleByDoctorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    days_of_week = serializers.CharField()
    start = serializers.TimeField()
    end = serializers.TimeField()

class SchedulerDoctorSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer()
    doctor = DoctorSerializer()    
    class Meta:
        model = Scheduler_Doctor
        # fields = '__all__'
        fields = ['id', 'schedule', 'doctor']
        # fields = ['id', 'doctor_id', 'schedule_id', 'schedule', 'doctor']

class GetSchedulerSerializer(serializers.Serializer):
    morning = ScheduleByDoctorSerializer(many=True)
    afternoon = ScheduleByDoctorSerializer(many=True)
    evening = ScheduleByDoctorSerializer(many=True)

class AppointmentSerializer(serializers.ModelSerializer):
    schedule_doctor = SchedulerDoctorSerializer()
    # user = UserSerializer()
    class Meta:
        model = Appointment
        fields = ['id', 'user_id', 'schedule_doctor', 'date', 'time', 'status', 'rating']
        # fields = '__all__'

class GetAppointmentSerializer(serializers.Serializer):
    coming = AppointmentSerializer(many=True)
    not_confirm = AppointmentSerializer(many=True)
    confirmed = AppointmentSerializer(many=True)
    cancel = AppointmentSerializer(many=True)

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = '__all__'
    

import hashlib
def hash_password(password):
    salt = "random string to make the hash more secure"
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password
    
class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'password', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'password', 'email']

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['refresh_token']

class BookingSerializer(serializers.ModelSerializer):
    id_doctor = serializers.IntegerField()
    id_schedule = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
