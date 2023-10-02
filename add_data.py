import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hibacsi.settings")  # Thay thế 'your_project' bằng tên thực tế của project Django

# Bắt buộc phải gọi django.setup() trước khi import các model
django.setup()

# Import các model từ ứng dụng 'app'
from app.models import Account

# Bây giờ bạn có thể thêm dữ liệu vào cơ sở dữ liệu bằng các lệnh tương tự như trong Django shell
account = Account(username="user1", password="password1", email="user1@example.com")
account.save()




from app.models import User

user = User(name="John Doe", gender=True, phone="1234567890", address="123 Main St", birthday="1990-01-01")
user.save()



from app.models import Doctor

doctor = Doctor(name="Dr. Smith", address="456 Elm St", id_specialty=1, id_hospital=1, phone="9876543210", 
                birthday="1980-05-15", gender=True, years_of_experience=10, descripe="Experienced doctor", rate=4.5)
doctor.save()



from app.models import Hospital

hospital = Hospital(name="General Hospital", email="info@hospital.com", address="789 Oak St")
hospital.save()




from app.models import Specialty

specialty = Specialty(name="Cardiology", descripe="Heart-related specialties")
specialty.save()



from app.models import Service

service = Service(name="Cardiac Exam", descripe="Heart examination service")
service.save()



from app.models import Schedule, Doctor

doctor = Doctor.objects.get(id=1)  # Thay đổi id theo tùy chỉnh của bạn
schedule = Schedule(id_doctor=doctor, days_of_week="2345678", start="08:00:00", end="16:00:00")
schedule.save()




from app.models import Appointment, User, Schedule
from datetime import date, time

user = User.objects.get(id=1)  # Thay đổi id theo tùy chỉnh của bạn
schedule = Schedule.objects.get(id=1)  # Thay đổi id theo tùy chỉnh của bạn
appointment = Appointment(id_user=user, id_schedule=schedule, date=date.today(), time=time(10, 0))
appointment.save()




from app.models import ServiceDoctor, Service, Doctor

service = Service.objects.get(id=1)  # Thay đổi id theo tùy chỉnh của bạn
doctor = Doctor.objects.get(id=1)  # Thay đổi id theo tùy chỉnh của bạn
service_doctor = ServiceDoctor(id_service=service, id_doctor=doctor)
service_doctor.save()


from app.models import Tool

tool = Tool(name="Calculator", description="A simple calculator tool", formula="a + b", questions={"question": "What is 2 + 2?"})
tool.save()
