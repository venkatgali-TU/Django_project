import sys

import urllib3
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import generics, mixins

# Create your views here.
from .forms import MvpForm, TeleOptiUserRequestForm, OverTimeUserRequestForm
from .models import Mvp
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import csv, io
from django.shortcuts import render
from django.contrib import messages
# Create your views here.
# one parameter named request

from .serializers import *

CRITICAL = 50
MESSAGE = "Enter the values in the portal below"
EMAIL = ""


def hello_mvp(request):
    # if this is a POST request we need to process the form data

    print(MvpForm(request.POST).errors)
    if request.method == 'POST' and MvpForm(request.POST).is_valid():
        # create a form instance and populate it with data from the request:
        #############
        if not request.user.is_authenticated:
            form = MvpForm()
            context = {}
            context['form'] = form
            messages.warning(request, " Please login to the Gmail accoun to continue")
            return render(request, "mvp/home.html", context)

        #############

        form = MvpForm(request.POST)
        # check whether it's valid:

        form.full_clean()
        form.fields
        mvp_model = form.save()
        print(form.clean_req_type())
        if 'Single' in form.clean_user_req():

            if form.clean_req_type() == "OverTime":
                return HttpResponseRedirect('/single/' + str(mvp_model.id) + '/OverTime')
            else:
                return HttpResponseRedirect('/single/' + str(mvp_model.id) + '/TeleOpti')
        else:
            # context = {}
            if form.clean_req_type() == "OverTime":
                return HttpResponseRedirect('/multi/' + str(mvp_model.id) + '/OverTime')
            else:
                return HttpResponseRedirect('/multi/' + str(mvp_model.id) + '/TeleOpti')

        # return HttpResponseRedirect('/mvp_app/')

    # if a GET (or any other method) we'll create a blank form
    else:
        if request.user.is_authenticated:
            username = str(request.user.email).replace("@", "%40")
        else:
            username = "Please login to continue"

        if not MvpForm(request.POST).is_valid():
            if "This field is required." in str(MvpForm(request.POST).errors):
                if "Please" not in username:
                    final_url = "https://epmsapi.taskus.prv/v1/api/employees/email/" + username  # 3054204"
                    final_headers = {
                        "x-api-key": "lsUfB4oaUX"
                    }
                    try:
                        global EMAIL
                        # fin = requests.get(final_url, final_headers, False)
                        # print(username[5:])
                        fin = requests.get(final_url, headers=final_headers, verify=False)

                        # temp_data_json = json.loads(json.dumps(fin.json()))

                        temp_data_json = json.loads(json.dumps(fin.json()))
                        EMAIL = str(temp_data_json['email'])
                        messages.warning(request, " ID : " + str(temp_data_json['id']))
                        messages.warning(request, " First Name : " + str(temp_data_json['firstName']))
                        messages.warning(request, " Last Name : " + str(temp_data_json['lastName']))
                        messages.warning(request, " Email : " + str(temp_data_json['email']))
                        messages.warning(request, " Supervisor Email : " + str(temp_data_json['supervisorEmployeeId']))
                        messages.warning(request, " Position : " + str(temp_data_json['position']['name']))
                        messages.warning(request, " Site : " + str(temp_data_json['site']['name']))
                        messages.warning(request, " Country Code : " + str(temp_data_json['site']['countryCode']))
                        messages.warning(request, " Location : " + str(temp_data_json['site']['location']))
                        messages.warning(request, " Time Zone : " + str(temp_data_json['site']['timeZone']))
                        messages.warning(request, " Campaign : " + str(temp_data_json['campaign']['name']))
                    except ConnectionError and KeyError:
                        messages.warning(request, " Couldn't identify your profile! " + str(username))
                        print("connection refused")

                else:
                    messages.warning(request, username)

            else:
                messages.warning(request, str(MvpForm(request.POST).errors), fail_silently=True)
            form = MvpForm()
            context = {}
            context['form'] = form
            return render(request, "mvp/home.html", context)

        # form = MvpForm()
        # context = {}
        # context['form'] = form
        # Mvp.objects.filter(emp_ID=request.user.username).update(emp_ID=username)
        # return render(request, "mvp/home.html", context)


def data_view(request):
    if request.method == "POST":
        key = request.POST['key']
        print(" success data : " + request.POST['key'])
        all_objects = MvpUserRequest.objects.all().filter(Name__contains=key)
        paginator = Paginator(all_objects, 35)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        return render(request, 'mvp/data.html', {'posts': posts})
    else:
        final_url = "https://epmsapi.taskus.prv/v1/api/employees?take=40000"
        final_headers = {
            "x-api-key": "lsUfB4oaUX"
        }
        final_list = {}
        fin = requests.get(final_url, headers=final_headers, verify=False)
        temp_data_json = json.loads(json.dumps(fin.json()))
        for item in temp_data_json:
            try:
                temp_camp = item['campaign']['name']
                final_list[item['employeeNo']] = temp_camp
            except TypeError:
                continue
        all_objects = MvpUserRequest.objects.all().order_by('-id')
        print(len(final_list))
        for objs in all_objects:
            try:
                if objs.Timezone == '':
                    MvpUserRequest.objects.filter(id=objs.id).update(
                        Timezone=final_list[objs.user_ID])
            except:
                continue

        paginator = Paginator(all_objects, 35)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        return render(request, 'mvp/data.html', {'posts': posts})


def single_user(request, mvp_id, req):
    global MESSAGE
    # print("req is :" + req)
    if req == "OverTime":
        if request.method == 'POST':  # and OverTimeUserRequestForm(request.POST).is_valid():
            if OverTimeUserRequestForm(request.POST).is_valid():

                # print("IN HERE!!!")
                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()
                form.for_Name()
                breaktime = form.for_break()
                print("breaktime" + breaktime)

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    form = OverTimeUserRequestForm()

                    context = {}
                    context['form'] = form
                    return render(request, "mvp/single.html", context)
                else:
                    mvp_model = form.save()
                    print('mvp_id is :' + str(MvpUserRequest.objects.latest('id').id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-SOT-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-SOT-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=breaktime)

                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    context = {'user_ID': 'WFM-IRA-SOT-' + str(mvp_id)}
                    send_mail('WFM - Plotting website submissions: ',
                              "Request Id : " + 'WFM-IRA-SOT-' + str(mvp_id) + " " + MESSAGE.replace(
                                  "Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              [EMAIL])
                    MESSAGE = ""
                    return render(request, "mvp/thanks.html", context)


            else:
                result = "Invalid form"

                if "This field is required." in str(OverTimeUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the required fields", fail_silently=True)
                else:
                    messages.warning(request, str(OverTimeUserRequestForm(request.POST).errors), fail_silently=True)
                form = OverTimeUserRequestForm(request.POST)
                context = {}
                context['form'] = form
                return render(request, "mvp/single.html", context)

        else:
            mvp_model = Mvp.objects.get(id=mvp_id)
            form = OverTimeUserRequestForm()
            context = {}
            context['form'] = form

            return render(request, "mvp/single.html", context)
    else:
        if request.method == 'POST':  # and TeleOptiUserRequestForm(request.POST).is_valid():
            if TeleOptiUserRequestForm(request.POST).is_valid():
                print("IN HERE!!!")
                form = TeleOptiUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()
                form.for_Name()

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    form = TeleOptiUserRequestForm()

                    context = {}
                    context['form'] = form
                    return render(request, "mvp/single.html", context)
                else:
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : "
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    mvp_model = form.save()
                    print('mvp_id is :' + str(MvpUserRequest.objects.latest('id').id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-STEL-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-STEL-' + str(mvp_id))
                    context = {'user_ID': 'WFM-IRA-STEL-' + str(mvp_id)}
                    send_mail('WFM - Plotting website submissions: ',
                              "Request Id : " + 'WFM-IRA-STEL-' + str(mvp_id) + " " + MESSAGE.replace(
                                  "Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              [EMAIL])
                    MESSAGE = ""
                    return render(request, "mvp/thanks.html", context)
            else:
                if "This field is required." in str(TeleOptiUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(TeleOptiUserRequestForm(request.POST).errors), fail_silently=True)
                    # messages.warning(request, re.search('<li>(.*)</li>', str(TeleOptiUserRequestForm(request.POST).errors).replace("__all__","")).group(1), fail_silently=True)
                form = TeleOptiUserRequestForm(request.POST)
                context = {}
                context['form'] = form
                return render(request, "mvp/single.html", context)

        else:
            mvp_model = Mvp.objects.get(id=mvp_id)
            form = TeleOptiUserRequestForm()
            context = {}
            context['form'] = form
            return render(request, "mvp/single.html", context)


def multi_user(request, mvp_id, req):
    global MESSAGE
    if req == "OverTime":
        if request.method == 'POST' and OverTimeUserRequestForm(request.POST).is_valid():
            if '_con' in request.POST:
                print("IN HERE!!!")
                print(request.POST)
                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()
                breaktime = form.for_break()

                ############

                form.for_Name()

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    new_form = OverTimeUserRequestForm()
                    context = {}
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)
                else:
                    mvp_model = form.save()
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MOT-S-' + str(mvp_id))
                    context = {}

                    new_form = OverTimeUserRequestForm()
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-MOT-S-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=breaktime)

                    return render(request, "mvp/multi.html", context)

                #################


            elif '_submit' in request.POST:

                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()
                breaktime = form.for_break()

                ############

                form.for_Name()

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    new_form = OverTimeUserRequestForm()
                    context = {}
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)
                else:
                    mvp_model = form.save()
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MOT-E' + str(mvp_id))
                    context = {}

                    new_form = OverTimeUserRequestForm()
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")

                    for mess in mess_split:
                        messages.success(request, mess)

                    context = {'user_ID': 'WFM-IRA-MOT-E' + str(mvp_id)}
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-MOT-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=breaktime)
                    send_mail('WFM - Plotting website submissions: ',
                              "Request Id : " + 'WFM-IRA-MOT-' + str(mvp_id) + " " + MESSAGE.replace(
                                  "Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              [EMAIL])
                    MESSAGE = ""
                    return render(request, "mvp/thanks.html", context)

                #################
        else:
            if not OverTimeUserRequestForm(request.POST).is_valid() and request.method == 'POST':
                if "This field is required." in str(OverTimeUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(OverTimeUserRequestForm(request.POST).errors), fail_silently=True)
                form = OverTimeUserRequestForm(request.POST)
                context = {}
                context['form'] = form
                return render(request, "mvp/multi.html", context)
            else:
                mvp_model = Mvp.objects.get(id=mvp_id)
                form = OverTimeUserRequestForm()
                context = {}
                context['form'] = form
                messages.info(request, MESSAGE, fail_silently=True)

                return render(request, "mvp/multi.html", context)

    else:
        if request.method == 'POST' and TeleOptiUserRequestForm(request.POST).is_valid():

            if '_con' in request.POST:
                print("IN HERE!!!")
                print(request.POST)
                form = TeleOptiUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()

                ############

                form.for_Name()

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    new_form = TeleOptiUserRequestForm()
                    context = {}
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : "
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)
                else:
                    mvp_model = form.save()
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MTEL-S' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-MTEL-S' + str(mvp_id))

                    context = {}

                    new_form = TeleOptiUserRequestForm()
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : "
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)

                #################
            elif '_submit' in request.POST:
                form = TeleOptiUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()

                ############

                form.for_Name()

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    new_form = TeleOptiUserRequestForm()
                    context = {}
                    context['form'] = new_form
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : "
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)
                else:
                    mvp_model = form.save()
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MTEL-E' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-MTEL-E' + str(mvp_id))
                    context = {}

                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                        form.cleaned_data['user_ID']) + " Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " Start time : " + str(
                        form.cleaned_data['Start_Time']) + " End Date : " + str(
                        form.cleaned_data['End_Date']) + " End Time : " + str(
                        form.cleaned_data['End_Time']) + " Activity : " + str(
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : "
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    context = {'user_ID': 'WFM-IRA-MTEL-' + str(mvp_id)}
                    send_mail('WFM - Plotting website submissions: ',
                              "Request Id : " + 'WFM-IRA-MTEL-' + str(mvp_id) + " " + MESSAGE.replace(
                                  "Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              [EMAIL])
                    MESSAGE = ""

                    return render(request, "mvp/thanks.html", context)

                #################
        else:
            if not TeleOptiUserRequestForm(request.POST).is_valid() and request.method == 'POST':
                if "This field is required." in str(TeleOptiUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(TeleOptiUserRequestForm(request.POST).errors), fail_silently=True)
                form = TeleOptiUserRequestForm(request.POST)
                context = {}
                context['form'] = form
                return render(request, "mvp/multi.html", context)
            else:
                mvp_model = Mvp.objects.get(id=mvp_id)
                form = TeleOptiUserRequestForm()
                context = {}
                context['form'] = form
                messages.info(request, MESSAGE, fail_silently=True)
                return render(request, "mvp/multi.html", context)


def profile_upload(request):
    # declaring template
    template = "mvp/profile_upload.html"
    data = MvpUserRequest.objects.all().order_by('-id')
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Download the template as a CSV, enter data and upload the CSV',
        'profiles': data
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)

    try:
        csv_file = request.FILES['file']
        # let's check if it is a csv file
        if not csv_file.name.endswith('.csv'):
            prompt['order'] = "Please upload a valid CSV!"
            return render(request, template, prompt)
        data_set = csv_file.read().decode('UTF-8')
        # setup a stream which is when we loop through each line we are able to handle a data in a stream
        io_string = io.StringIO(data_set)
        next(io_string)
        count = 0
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            count = count + 1
            req_id = MvpUserRequest.objects.latest('id').id
            # print(column)
            if count != 1:
                tmp_column = check(column)
                # print(count)
                if "Invalid" not in tmp_column:
                    if column[6] == '':
                        request_ID_str = "WFM-IRA-MTEL-" + str(req_id)
                    else:
                        request_ID_str = "WFM-IRA-MOT-" + str(req_id)

                    _, created = MvpUserRequest.objects.update_or_create(
                        user_ID=column[0],
                        Name=request_ID_str,
                        Start_Date=column[1],
                        End_Date=column[2],
                        Start_Time=column[3],
                        End_Time=column[4],
                        Activity=column[5],
                        Mul_Over=column[6],
                        Timezone='',
                        BreakTime=tmp_column,
                        Status='In Progress'
                    )
                else:
                    prompt['order'] = tmp_column
                    return render(request, template, prompt)

        prompt['order'] = "Success! Please check your status in submitted tasks list"
        return render(request, template, prompt)
    except Exception as e:
        print(str(e))
        prompt['order'] = str(e)
        return render(request, template, prompt)


def help_needed(request):
    # declaring template
    template = "mvp/help_needed.html"
    data = MvpUserRequest.objects.all().order_by('-id')
    # prompt is a context variable that can have different values      depending on their context
    if len(data) == 0:
        order_str = "No records to show"
    else:
        order_str = "Please find all the tickets need help"

    prompt = {
        'order': 'Download the template as a CSV, enter data and upload the CSV',
        'profiles': data
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)


def check(column):
    user_id = column[0]
    str_time = column[3]
    end_time = column[4]
    str_date = column[1]
    end_date = column[2]
    activity = column[5]
    Mul_Over = column[6]
    timezone = ""
    Status = ""
    result = ""

    if user_id and str_time and end_time:
        # Only do something if both fields are valid so far.
        str_date = datetime.strptime(str_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        past = datetime.now() - timedelta(days=7)
        if len(user_id) != 7:
            return "Invalid user ID"
        else:
            if str_date < past or end_date < past:
                pass
                # return "Invalid Dates"
            else:
                if str_date > end_date:
                    return "Invalid dates"
                else:
                    if len(str_time) != 5 and ":" not in str_time:
                        return "Invalid start time"
                    else:
                        str_time_split = str_time.split(":")
                        str_hour = str_time_split[0]
                        str_min = str_time_split[1]
                        try:
                            str_hour = int(str_hour)
                            str_min = int(str_min)

                            # print(str(str_hour))
                            # print(str(str_min))
                            if str_hour > 23 or str_hour < 0 or str_min > 59 or str_min < 0:
                                return "Invalid start time"
                            else:
                                if len(end_time) != 5 and ":" not in end_time:

                                    return "Invalid end time"
                                else:
                                    # print(str_time)
                                    end_time_split = end_time.split(":")
                                    end_hour = end_time_split[0]
                                    end_min = end_time_split[1]
                                    try:
                                        end_hour = int(end_hour)
                                        end_min = int(end_min)
                                        if end_hour > 23 or end_hour < 0 or end_min > 59 or end_min < 0:
                                            return "Invalid end time"
                                        else:
                                            try:
                                                start_time_date = datetime.strptime(str_time, '%H:%M')
                                                end_time_date = datetime.strptime(end_time, '%H:%M')
                                                print(start_time_date)
                                                print(end_time_date)
                                                if start_time_date > end_time_date:
                                                    return "Invalid  start or end time"
                                                else:
                                                    print("here")

                                                    final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(
                                                        user_id)  # 3054204"
                                                    final_headers = {
                                                        "x-api-key": "lsUfB4oaUX"
                                                    }
                                                    try:
                                                        # fin = requests.get(final_url, final_headers, False)
                                                        # print(username[5:])
                                                        fin = requests.get(final_url, headers=final_headers,
                                                                           verify=False)

                                                        # temp_data_json = json.loads(json.dumps(fin.json()))

                                                        temp_data_json = json.loads(json.dumps(fin.json()))
                                                        country = str(temp_data_json['site']['countryCode'])
                                                        breaktime = ""

                                                        if country == 'US':
                                                            temp_time = (((
                                                                                  end_time_date - start_time_date).seconds / 60) / 60)
                                                            if temp_time == 9:
                                                                breaktime = 'lunch(30) + 15 + 15 + 15'
                                                            elif temp_time < 9 and temp_time >= 8:
                                                                breaktime = 'lunch(30) + 15 + 15'
                                                            elif temp_time < 8 and temp_time >= 7:
                                                                breaktime = 'lunch(30) + 15'
                                                            elif temp_time < 7 and temp_time >= 6:
                                                                breaktime = 'lunch(30) + 15'
                                                            elif temp_time < 6 and temp_time >= 5:
                                                                breaktime = 'lunch(30) + 15'

                                                            elif temp_time < 5 and temp_time >= 2:
                                                                breaktime = '15'
                                                            elif temp_time < 2 and temp_time >= 1:
                                                                breaktime = 'No break'

                                                        elif country == 'PH':
                                                            temp_time = (((
                                                                                  end_time_date - start_time_date).seconds / 60) / 60)
                                                            if temp_time == 12:
                                                                breaktime = '15 + 15 + 15 + lunch(60)'
                                                            elif temp_time < 12 and temp_time >= 11:
                                                                breaktime = '15 + 15 + 11 + lunch(60)'
                                                            elif temp_time < 11 and temp_time >= 10:
                                                                breaktime = '15 + 15 + 7 + lunch(60)'
                                                            elif temp_time < 10 and temp_time >= 9:
                                                                breaktime = '15 + 15 + 5 + lunch(60)'
                                                            elif temp_time < 9 and temp_time >= 8:
                                                                breaktime = '15 + 15 + lunch(30)'
                                                            elif temp_time < 8 and temp_time >= 7:
                                                                breaktime = '15 + 11'
                                                            elif temp_time < 7 and temp_time >= 6:
                                                                breaktime = '15 + 7'
                                                            elif temp_time < 6 and temp_time >= 5:
                                                                breaktime = '15 + 5'
                                                            elif temp_time < 5 and temp_time >= 4:
                                                                breaktime = '15'
                                                            elif temp_time < 4 and temp_time >= 3:
                                                                breaktime = '11'
                                                            elif temp_time < 3 and temp_time >= 2:
                                                                breaktime = '7'
                                                            elif temp_time < 2 and temp_time >= 1:
                                                                breaktime = 'No break'
                                                        else:
                                                            temp_time = (((
                                                                                  end_time_date - start_time_date).seconds / 60) / 60)
                                                            if temp_time == 9:
                                                                breaktime = 'lunch(30) + 15 + 15 + 15'
                                                            elif temp_time < 9 and temp_time >= 8:
                                                                breaktime = 'lunch(30) + 15 + 15'
                                                            elif temp_time < 8 and temp_time >= 7:
                                                                breaktime = 'lunch(30) + 15'
                                                            elif temp_time < 7 and temp_time >= 6:
                                                                breaktime = 'lunch(30) + 15'
                                                            elif temp_time < 6 and temp_time >= 5:
                                                                breaktime = 'lunch(30) + 15'

                                                            elif temp_time < 5 and temp_time >= 2:
                                                                breaktime = '15'
                                                            elif temp_time < 2 and temp_time >= 1:
                                                                breaktime = 'No break'
                                                        result = breaktime

                                                    except ConnectionError and KeyError:
                                                        return "Invalid User ID"

                                            except ValueError:
                                                return "Invalid Start time or End time"
                                    except ValueError:
                                        return 'Invalid end time'

                        except ValueError:
                            return 'Invalid start time'

                            #####################################

    else:
        return 'Please enter valid user ID'
        # raise ValidationError(
        #     "Not a valid input, Please try again with correct input"
        # )
    return result


@api_view(['GET', 'POST'])
def request_list(request):
    """
    List all products, or create a new product.
    """
    if request.method == 'GET':
        products = MvpUserRequest.objects.all().exclude(Status__contains='omplete').order_by('-id')[:15]
        serializer = MvpSerializer(products, context={'request': request}, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MvpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def request_detail(request, pk):
    """
    Retrieve, update or delete a product instance.
    """
    try:
        product = MvpUserRequest.objects.get(pk=pk)
    except MvpUserRequest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MvpSerializer(product, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MvpSerializer(product, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MvpViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                 generics.GenericAPIView):  # viewsets.ModelViewSet):
    queryset = MvpUserRequest.objects.all().order_by('-id')[:20]
    # last_ten_in_ascending_order = reversed(last_ten)
    # queryset = MvpUserRequest.objects.reverse()[:2]
    serializer_class = MvpSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
