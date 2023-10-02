from django.db import models

# Create your models here.

class Account(models.Model):
    
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    #role : user, admin, doctor, hospital
    role = models.CharField(max_length=10, default='user')
    id_role = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.username

class User(models.Model):
    
    name = models.CharField(max_length=255)
    gender = models.BooleanField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'UserInfo #{self.id}'



class Doctor(models.Model):

    
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    id_specialty = models.IntegerField()  # Thay thế bằng khoá ngoại đến model Chuyên khoa (Specialty)
    id_hospital = models.IntegerField()  # Thay thế bằng khoá ngoại đến model Bệnh viện (Hospital)
    phone = models.CharField(max_length=20)
    birthday = models.DateField()
    gender = models.BooleanField()
    years_of_experience = models.IntegerField()
    descripe = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Sử dụng DecimalField cho tiền tối ưu

    def __str__(self):
        return self.name


class Hospital(models.Model):
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Specialty(models.Model):
    
    name = models.CharField(max_length=255)
    descripe = models.TextField()

    def __str__(self):
        return self.name
    
class Service(models.Model):
    
    name = models.CharField(max_length=255)
    descripe = models.TextField()

    def __str__(self):
        return self.name    

class Schedule(models.Model):

    id_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    days_of_week = models.CharField(max_length=7)  # CharField để lưu trữ chuỗi ngày (ví dụ: "2345678")
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return f"Lịch làm việc của Bác sĩ {self.id_doctor} vào các ngày {self.days_of_week} từ {self.start} đến {self.end}"
    
class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Khoá ngoại liên kết đến User
    id_schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)  # Khoá ngoại liên kết đến Schedule
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"Lịch hẹn ngày {self.date} vào {self.time}"
    
class ServiceDoctor(models.Model):
    id_service = models.ForeignKey(Service, on_delete=models.CASCADE)
    id_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Dịch vụ {self.id_service} của Bác sĩ {self.id_doctor}"
    

from django.db.models import JSONField

class Tool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    formula = models.CharField(max_length=255)
    questions = JSONField()

    def __str__(self):
        return self.name