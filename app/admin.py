from django.contrib import admin
from .models import Account, User, Doctor, Hospital, Specialty, Service, Schedule, Appointment, ServiceDoctor, Tool

admin.site.register(Account)
admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Hospital)
admin.site.register(Specialty)
admin.site.register(Service)
admin.site.register(Schedule)
admin.site.register(Appointment)
admin.site.register(ServiceDoctor)
admin.site.register(Tool)
