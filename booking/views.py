import datetime
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
# serializers
from app.serializers import BookingSerializer, AppointmentSerializer
# permissions
from app.permissions import IsAdminPermission, IsDoctorPermission, IsHospitalPermission, IsUserPermission
from rest_framework.decorators import authentication_classes, permission_classes
from app.models import User, Scheduler_Doctor, Appointment
from rest_framework import status


# Create your views here.

@permission_classes([IsUserPermission])
class BookingView(GenericAPIView):
    serializer_class = BookingSerializer
    def post(self, request):
        data = request.data
        id_doctor = data.get('id_doctor', '')
        id_schedule = data.get('id_schedule', '')
        date = data.get('date', '')
        if (id_doctor == '' or id_schedule == '' or date == ''): 
            return Response({'detail': 'Empty data: need id_doctor, id_schedule, date'}, status=status.HTTP_400_BAD_REQUEST)
        date = datetime.datetime.strptime(date, '%Y/%m/%d').date()
        if (date < datetime.date.today()):
            return Response({'detail': 'Date is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        print(date, data)
        # get user by account
        user = User.objects.get(account=request.account)
        # check user has phone number
        if (user.phone == ''):
            return Response({'detail': 'User has not phone number'}, status=status.HTTP_400_BAD_REQUEST)
        # check user has address
        if (user.address == ''):
            return Response({'detail': 'User has not address'}, status=status.HTTP_400_BAD_REQUEST)
        # get Schedule_Doctor by id_doctor and id_schedule
        scheduleDoctor = Scheduler_Doctor.objects.get(id_doctor_id=id_doctor, id_schedule_id=id_schedule)
        # check Schedule_Doctor is not null
        if (scheduleDoctor == None):
            return Response({'detail': 'Schedule_Doctor does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        # check Schedule_Doctor is not full
        is_full = Appointment.objects.filter(id_schedule_doctor=scheduleDoctor, date=date).count() > 0
        if (is_full):
            return Response({'detail': 'Schedule_Doctor is full'}, status=status.HTTP_400_BAD_REQUEST)
        # create Booking
        appointment = Appointment.objects.create(id_schedule_doctor=scheduleDoctor, id_user=user, date=date)
        appointment.save()
        appointment = AppointmentSerializer(appointment)
        # return Booking
        return Response(appointment.data, status=status.HTTP_201_CREATED)

