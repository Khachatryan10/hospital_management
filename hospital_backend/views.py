from .models import Schedule, MedicalHistory, Notification
from django.shortcuts import render, HttpResponse
from .models import User, Schedule
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import json
import re
# from django.db.models import Q
# import datetime
# import time
from django.utils import timezone

from dotenv import load_dotenv
import os
# Create your views here.

load_dotenv()


def reregisterUser(request):
    return render(request, "index.html")


def registerUserPost(request):
    if request.method == "POST":
        user_data = json.loads(request.body)

        name = user_data.get("name")
        last_name = user_data.get("lastName")
        email = user_data.get("email")
        role = user_data.get("role")
        speciality = user_data.get("speciality")
        regist_code_doctor = user_data.get("registCodeDoctor")
        regist_code_receptionist = user_data.get("registCodeReceptionist")
        phone_number = user_data.get("phoneNumber")
        password = user_data.get("password")
        confirmation = user_data.get("confirmation")

        containsNumber = re.search(r"\d", password)
        containsCapitalLetter = re.search(r"[A-Z]", password)
        containsSmallLetter = re.search(r"[a-z]", password)
        containsSpecificCharacter = re.search(
            r"[/,?(){}_[\]#\-*+<>|;:!'\".\\$~@`]", password)
        matches_all = containsNumber and containsCapitalLetter and containsSmallLetter and containsSpecificCharacter

        numberFormatRegex = re.search(
            r"[0][0-9]{1}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", phone_number)
        emailRegex = re.search(
            r"^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$", email)

        if not matches_all or not numberFormatRegex or not emailRegex:
            return HttpResponse("Please fill the inputs with appropriate format", status=400)

        code_recep = os.environ.get('CODE_RECEP')
        code_doctor = os.environ.get('CODE_DOCTOR')

        if role == "Receptionist" and regist_code_receptionist != code_recep or role == "Receptionist" and not regist_code_receptionist:
            return HttpResponse("Please provide valid code", status=401)

        if role == "Doctor" and regist_code_doctor != code_doctor or role == "Doctor" and not regist_code_doctor:
            return HttpResponse("Please provide valid code", status=401)

        if role == "Doctor" and not speciality:
            return HttpResponse("Select Speciality field", status=422)

        """ if user selects role Doctor then selects sepciality,
        but switches to register as patient the selected value remains. 
        Since patients must not have speciality (it's only for doctors), 
        if this happens speciality will be set to an empty string. """

        if role == "Patient" and speciality:
            speciality = ""
        if password == confirmation:
            try:
                new_user = User.objects.create_user(email=email, role=role, speciality=speciality,
                                                    first_name=name, last_name=last_name, phone_number=phone_number, password=password)
                new_user.save()
                return HttpResponse("Sucessfully registered user", status=200)

            except IntegrityError:
                return HttpResponse("Email already taken", status=409)
        else:
            return HttpResponse("Passwords don't match", status=422)
    else:
        return HttpResponse("This url is only for POST requests")


def loginUserPage(request):
    return render(request, "index.html")


def profile(request):
    return render(request, "index.html")


def appointements(request):
    return render(request, "index.html")


def loginUser(request):
    if request.method == "POST":
        login_data = json.loads(request.body)
        email = login_data.get("email")
        password = login_data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse("Successfully logged in", status=200)
        else:
            return HttpResponse("Email and/or password are incorrect", status=403)
    else:
        HttpResponse("This url is only for POST requests")


def user_data(request):
    is_authenticated = request.user.is_authenticated
    current_user = request.user
    data = {}

    if is_authenticated:
        data = current_user.serialize()
    else:
        data = {}

    return JsonResponse([data, {"is_authenticated": is_authenticated}], safe=False)


def logoutUser(request):
    logout(request)
    return render(request, "index.html")


def change_password(request):
    if request.method == "POST":
        user_data = json.loads(request.body)
        old_password = user_data.get("oldPassword")
        new_password = user_data.get("newPassword")
        new_password_confirmation = user_data.get("newPasswordConfirmation")

        containsNumber = re.search(r"\d", new_password)
        containsCapitalLetter = re.search(r"[A-Z]", new_password)
        containsSmallLetter = re.search(r"[a-z]", new_password)
        containsSpecificCharacter = re.search(
            r"[/,?(){}_[\]#\-*+<>|;:!'\".\\$~@`]", new_password)
        matches_all = containsNumber and containsCapitalLetter and containsSmallLetter and containsSpecificCharacter

        user = authenticate(email=request.user.email, password=old_password)

        if not matches_all:
            return HttpResponse("Please fill password with appropriate format", status=400)

        if old_password == new_password:
            return HttpResponse("New password can't be the same as the old one", status=409)

        if user is None:
            return HttpResponse("Wrong password", status=401)

        if new_password != new_password_confirmation:
            return HttpResponse("Password and confirmation mismatch", status=422)

        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return HttpResponse("Success")
        else:
            return HttpResponse("Something went wrong")

    else:
        return HttpResponse("This url is only for POST requests")


def delete_account(request):
    if request.method == "DELETE":
        user_data = json.loads(request.body)
        password = user_data.get("deleteAccountPassword")
        user = authenticate(password=password, email=request.user.email)

        if user is None:
            return HttpResponse("Wrong Password", status=401)

        if user is not None:
            user.delete()
            return HttpResponse("Account sucessfully deleted")
    else:
        return HttpResponse("This url is only for DELETE requests")


def doctors(request):
    doctors_data = User.objects.filter(role="Doctor")
    return JsonResponse([doctor.serialize() for doctor in doctors_data], safe=False)


def doctor_page(request, id):
    return render(request, "index.html")


def doctor_data(request, id):
    try:
        doctor_data = User.objects.filter(role="Doctor").filter(id=id)
    except ValidationError:
        doctor_data = []

    return JsonResponse([data.serialize() for data in doctor_data], safe=False)


schedule_time = ["09:00", "09:20", "09:40", "10:00",
                 "10:20", "10:40", "11:00", "11:20",
                 "11:40", "12:00", "13:30", "13:50",
                 "14:10", "14:30", "14:50", "15:10",
                 "15:30", "15:50", "16:10", "16:30",
                 "16:50"]

week_days = ["Sunday", "Monday", "Tuesday",
             "Wednesday", "Thursday", "Friday", "Saturday"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "June",
          "July", "Aug",	"Sept",	"Oct", "Nov", "Dec"]

# require role patient


def add_appointement(request):
    if request.method == "POST":
        user_data = json.loads(request.body)
        patient_name = user_data.get("patientName")
        patient_last_name = user_data.get("patientLastName")
        doctor_name = user_data.get("doctorName")
        doctor_last_name = user_data.get("doctorLastName")
        doctor_email = user_data.get("doctorEmail")
        patient_email = user_data.get("patientEmail")
        # patient_id = user_data.get("patientID")
        doctor_id = user_data.get("doctorId")
        week_day = user_data.get("weekDay")
        appointement_date = user_data.get("appintementDate")
        appointement_time = user_data.get("appintementTime")
        password_appointement = user_data.get("passwordAppointement")

        user = authenticate(
            request, password=password_appointement, email=request.user.email)

        if not password_appointement:
            return HttpResponse("User not found", status=422)

        if user is None:
            return HttpResponse("User not found", status=404)

        try:
            occupied_appointement = Schedule.objects.filter(
                time=appointement_time, date=appointement_date, doctor_id=doctor_id)
        except ValidationError:
            return HttpResponse("Wrong time or date type", status=403)

        user_appointement_same_day = Schedule.objects.filter(
            patient_email=request.user.email, date=appointement_date, doctor_id=doctor_id, working_day=True)

        if user_appointement_same_day.exists():
            return HttpResponse("You already have an appointement for today", status=409)

        if occupied_appointement.exists():
            return HttpResponse("Appointement is already taken", status=400)

        if week_day == "Saturday" or week_day == "Sunday":
            return HttpResponse("Not working day", status=400)

        if request.user.role != "Patient":
            return HttpResponse("Only users with role patient can take an appointement", status=400)

        if appointement_time[:5] not in schedule_time:
            return HttpResponse("Wrong time for appointement", status=400)

        if week_day == "Saturday" or week_day == "Sunday":
            return HttpResponse("Wrong day for appointement", status=400)

        if week_day not in week_days:
            return HttpResponse("Wrong week day", status=400)

        if week_day not in week_days:
            return HttpResponse("Wrong week day", status=400)

        if not patient_email or not patient_name or not patient_last_name or not doctor_id or not week_day or not appointement_date or not appointement_time or not doctor_name or not doctor_last_name or not doctor_email:
            return HttpResponse("Please provide required data to add appointement", status=400)

        if appointement_time[:5] not in schedule_time:
            return HttpResponse("Wrong time", status=400)

        try:
            schedule = Schedule(patient_email=patient_email,
                                week_day=week_day, doctor_id=doctor_id,
                                patient_name=patient_name,
                                patient_last_name=patient_last_name,
                                working_day=True,
                                doctor_name=doctor_name, doctor_last_name=doctor_last_name, doctor_email=doctor_email,
                                date=appointement_date, time=appointement_time)
            schedule.save()
            return HttpResponse("Appontement is added", status=200)

        except ValidationError:
            return HttpResponse("Wrong time or date type", status=403)
    else:
        return HttpResponse("This url is only for POST requests")


def doctors_schedule(request, id):
    schedules = Schedule.objects.filter(doctor_id=id)
    return JsonResponse([{"time": schedule.time, "date": schedule.date, "working_day": schedule.working_day, "id": schedule.id, "week_day": schedule.week_day} for schedule in schedules], safe=False)


def my_appointements_data(request):
    if request.user.role == "Patient":
        try:
            schedules = Schedule.objects.filter(patient_email=request.user.email,working_day=True)
        except AttributeError:
            return HttpResponse("Please log in in order to be able to see your appointements")
    elif request.user.role == "Doctor":
        try:
            schedules = Schedule.objects.filter(
                doctor_email=request.user.email, working_day=True)
        except AttributeError:
            return HttpResponse("Please log in in order to be able to see your appointements")
    return JsonResponse([schedule.serialize() for schedule in schedules], safe=False)


def my_appointements(request):
    return render(request, "index.html")


def manage_appointements(request):
    return render(request, "index.html")


def my_schedule(request):
    schedules = Schedule.objects.filter(doctor_email=request.user.email)
    return JsonResponse([{"time": schedule.time, "date": schedule.date, "working_day": schedule.working_day, "id": schedule.id, "week_day": schedule.week_day} for schedule in schedules], safe=False)


def update_appointement(request):
    if request.method == "POST":
        schedules = json.loads(request.body)
        schedules_data = schedules.get("scheduleToUpdate")
        choice = schedules.get("choice")
        password = schedules.get("password")
        date_time = []
        date = []
        time = []

        # add if not schedule_data length respons httt response 400 and etc
        user = authenticate(
            request, password=password, email=request.user.email, role="Doctor")

        if not password:
            return HttpResponse("User not found", status=422)

        if user is None:
            return HttpResponse("User not found", status=404)
        
        if len(schedules_data) < 1:
            return HttpResponse("Missing Info", status=403)
        
        if not choice:
            return HttpResponse("missing choice", status=406)
        
        for data in schedules_data:
            date_time.append(
                {"date": data["date"], "time": data["time"], "week_day": data["weekDay"]})
        
        if choice == "notWDay":
            for dt in date_time:

                if dt["week_day"] == "Saturday" or dt["week_day"] == "Sunday":
                    return HttpResponse(status=400)
                
                if dt["week_day"] not in week_days:
                    return HttpResponse(status=400)

                if Schedule.objects.filter(
                    doctor_email=request.user.email, date=dt["date"], time=dt["time"]).exists():
                    Schedule.objects.filter(
                    doctor_email=request.user.email, date=dt["date"], time=dt["time"]).update(working_day=False)
                    sr = Schedule.objects.filter(
                        doctor_email=request.user.email, date=dt["date"], time=dt["time"],working_day=True)
                    sr.delete()
                else:
                    try:
                        schedule = Schedule(patient_email="",
                                            week_day=dt["week_day"], doctor_id=request.user.id,
                        working_day=False,
                        doctor_name=request.user.first_name, doctor_last_name=request.user.last_name, doctor_email=request.user.email,
                                            date=dt["date"], time=dt["time"])
                        schedule.save()
                    except ValidationError:
                        return HttpResponse("Failed to add schedule date",status=403)
        
        
            return HttpResponse("Done", status=200)
        elif choice == "wDay":
            for data in schedules_data:
                        date.append(data["date"])
                        time.append(data["time"])
                    
                # for dt in date_time:
            schedule = Schedule.objects.filter(
                        doctor_email=request.user.email, date__in=date, time__in=time)
            schedule.delete()
            return HttpResponse("Done", status=200)
        else:
            return HttpResponse("Wrong input",status=400)

    else:
        return HttpResponse("This url is only for POST requests")


def my_medical_history(request):
    return render(request, "index.html")


def add_medical_history_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        birth_date = data.get("birthDate")
        med_info = data.get("medInfo")

if not patient then don't let add medical history
        # try: 
        #     patient = User.objects.get(request, first_name=first_name, last_name=last_name, email=email)
        #     # if patient.exists():
        #     #     return HttpResponse(status=200)
            
        # except ValueError:
        # # if patient.exists()
        #     return HttpResponse(status=404)

        if not email or not first_name or not last_name or not birth_date or not med_info:
            return HttpResponse("Please fill all fields", status=400)

        # if patient.exists():

        
        mh = MedicalHistory.objects.filter(
            patient_name=first_name, patient_last_name=last_name, patient_email=email)

        if mh.exists():
            return HttpResponse("The patient already has a medical history, send a request to update it.", status=409)
        
        patient = User.objects.filter(email=email, first_name=first_name, last_name=last_name)
        

        try:
            if patient.exists():
                med_history = MedicalHistory(
                    patient_email=email, doctor_email=request.user.email, doctor_name=request.user.first_name,
                    doctor_last_name=request.user.last_name, patient_name=first_name, patient_last_name=last_name, patient_birth_date=birth_date,
                    medical_information=med_info)
                med_history.save()
                return HttpResponse("Medical history is added", status=200)
            else:
                return HttpResponse("No user found", status=404)
        except ValidationError:
            return HttpResponse("Failed to add medical history", status=403)

    else:
        return HttpResponse("This url is only POST requests")

def add_medical_history(request):
    return render(request, "index.html")


def get_medical_history_data(request):
    med_hostory_data = MedicalHistory.objects.all()
    return JsonResponse([med_info.serialize() for med_info in med_hostory_data], safe=False)

def get_my_medical_history(request):
    med_history = MedicalHistory.objects.filter(patient_email=request.user.email)
    return JsonResponse([data.serialize() for data in med_history], safe=False)

def save_notification(request):
    if request.method == "POST":
        data = json.loads(request.body)
        sender_email = data.get("sender")
        sender_name = data.get("senderName") 
        sender_last_name = data.get("senderLastName")  
        receiver_email = data.get("receiver")
        content = data.get("content")
        date = data.get("date")
        time = data.get("time")

        if not sender_email or not sender_name or not sender_last_name or not receiver_email or not content or not data or not time:
            return HttpResponse("missing information", status=404)

        receiver_user = User.objects.filter(
            email=receiver_email)
        
        try:
            if receiver_user.exists():
                n = Notification(sender=sender_email, sender_name=sender_name, sender_last_name=sender_last_name,
                                receiver=receiver_email, content=content, date=date, time=time)
                n.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse("User not found ",status=404)
        except ValidationError:
            return HttpResponse("Failed to send request", status=403)
    else:
        return HttpResponse("This url is only for POST requests")

# def notifs(request):
#     n = Notification.objects.all()
#     return JsonResponse([data.serialize() for data in n], safe=False)

def my_update_requests(request):
    n = Notification.objects.filter(sender=request.user.email)
    return JsonResponse([data.serialize() for data in n], safe=False)
