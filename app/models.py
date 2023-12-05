from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Account(models.Model):

    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    #role : user, admin, doctor, hospital
    role = models.CharField(max_length=10, default='user')
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to='media/', null=True)
    status = models.IntegerField(default=0)  # 0: còn hoạt động, 1: đã bị khóa
    def __str__(self):
        return self.username

class User(models.Model):

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='user', null=True)
    name = models.CharField(max_length=255)
    gender = models.BooleanField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'UserInfo #{self.id}'

class Admin(models.Model):

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='admin', null=True)
    name = models.CharField(max_length=255)
    gender = models.BooleanField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'AdminInfo #{self.id}'



class Hospital(models.Model):

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='hospital',null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    address_map = models.CharField(max_length=255, null=True, blank=True)
    CITY_CHOICES = [
        ('Hanoi', 'Hà Nội'),
        ('HoChiMinh', 'Hồ Chí Minh'),
        ('Danang', 'Đà Nẵng'),
        
        # Add the rest of the cities here
        # ('CityCode', 'CityName'),
    ]

    city = models.CharField(max_length=255, choices=CITY_CHOICES, null=True, blank=True)
    info = models.TextField(default='')


    def __str__(self):
        return self.name

class Specialty(models.Model):
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    name = models.CharField(max_length=255)
    describe = models.TextField()

    def __str__(self):
        return self.name

class Doctor(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='doctor', null=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    CITY_CHOICES = [
        ('Hanoi', 'Hà Nội'),
        ('HoChiMinh', 'Hồ Chí Minh'),
        ('Danang', 'Đà Nẵng'),
    ]

    city = models.CharField(max_length=255, choices=CITY_CHOICES, null=True, blank=True)
    # specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)  # Thay thế bằng khoá ngoại đến model Chuyên khoa (Specialty)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)  # Thay thế bằng khoá ngoại đến model Bệnh viện (Hospital)
    phone = models.CharField(max_length=20)
    birthday = models.DateField(null=True, blank=True)
    gender = models.BooleanField(null=True, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    describe = models.TextField(null=True, blank=True)
    num_of_rating = models.IntegerField(default=0)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])  # Sử dụng FloatField cho đánh giá
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Sử dụng DecimalField cho tiền tối ưu
    
    def __str__(self):
        return self.name

class SpecialtyDoctor(models.Model):
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Chuyên khoa {self.specialty} của Bác sĩ {self.doctor}"



class Service(models.Model):
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    name = models.CharField(max_length=255)
    descripe = models.TextField()

    def __str__(self):
        return self.name


class ServiceDoctor(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Dịch vụ {self.service} của Bác sĩ {self.doctor}"

class Schedule(models.Model):
    days_of_week = models.IntegerField() # 1:CN, 2:T2, 3:T3, 4:T4, 5:T5, 6:T6, 7:T7
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return f"Lịch làm việc vào các ngày {self.days_of_week} từ {self.start} đến {self.end}"

class Scheduler_Doctor(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    def __str__(self):
        return f"Lịch làm việc của Bác sĩ {self.doctor} trong khoảng thời gian {self.schedule}"

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Khoá ngoại liên kết đến User
    schedule_doctor = models.ForeignKey(Scheduler_Doctor, on_delete=models.CASCADE, default=0)  # Khoá ngoại liên kết đến Scheduler_Doctor
    date = models.DateField()
    time = models.TimeField(null=True)
    status = models.IntegerField(default=0) # 0: chưa xác nhận, 1: đã xác nhận, 2: đã hủy
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])  # Sử dụng FloatField cho đánh giá
    def __str__(self):
        return f"Lịch hẹn ngày {self.date} vào {self.time}"



from django.db.models import JSONField

class Tool(models.Model):
    icon = models.ImageField(upload_to='media/', null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    formula = models.CharField(max_length=255)
    questions = JSONField()

    def __str__(self):
        return self.name

class Category(models.Model):
    icon = models.ImageField(upload_to='media/', null=True)
    name = models.CharField(max_length=255)
    describe = models.TextField()

    def __str__(self):
        return self.name    

class Blog(models.Model):
    picture = models.ImageField(upload_to='media/', null=True)
    id_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='blogs')
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class Test(models.Model):
    time = models.TimeField()

    def __str__(self):
        return str(self.time)