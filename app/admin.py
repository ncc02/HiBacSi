from django.contrib import admin
from .models import *

admin.site.register(Account)

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Doctor)
admin.site.register(Hospital)

admin.site.register(Specialty)
admin.site.register(SpecialtyDoctor)

admin.site.register(Service)
admin.site.register(ServiceDoctor)

admin.site.register(Schedule)
admin.site.register(Scheduler_Doctor)
admin.site.register(Appointment)

admin.site.register(Tool)


admin.site.register(Test)