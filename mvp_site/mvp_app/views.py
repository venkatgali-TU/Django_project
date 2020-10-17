from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from .forms import MvpForm, TeleOptiUserRequestForm, OverTimeUserRequestForm
from .models import Mvp, MvpUserRequest
import argparse
import json
import requests
import simplejson as json
import re
from rest_framework import viewsets
from .serializers import MvpSerializer
from django.core.paginator import Paginator
from django.shortcuts import render
import json
import json

import gspread
import requests
import simplejson as json
from oauth2client.service_account import ServiceAccountCredentials
CRITICAL = 50
MESSAGE = "Enter the values in the portal below"

def login(json_key):
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)
    gc = gspread.authorize(credentials)
    return gc


def Sheets_Update(params):
    gc = login(r'C:\Users\vg3054204\Downloads\rpachatbot-283314-3f167aa77833.json')

    worksheet = gc.open_by_key("1pGHWuiQR8GmdByKY-PFhb3-xvg8UOnk_6kCm7SkvQ4o")
    to_get_count = worksheet.values_get(range='San Antonio!K1:K100000', params=None)['values']
    row_num = len(to_get_count)
    lister = []
    for obj in to_get_count:
        lister.append(obj)
    lister.pop(0)

    return lister


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
                        # fin = requests.get(final_url, final_headers, False)
                        # print(username[5:])
                        fin = requests.get(final_url, headers=final_headers, verify=False)

                        # temp_data_json = json.loads(json.dumps(fin.json()))

                        temp_data_json = json.loads(json.dumps(fin.json()))
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
    all_objects = MvpUserRequest.objects.all().order_by('-id')[:5]
    lister = Sheets_Update("s")
    try:
        if ":::" not in lister[0][0]:
            paginator = Paginator(all_objects, 5)
            page = request.GET.get('page')
            posts = paginator.get_page(page)
            print(Sheets_Update("s"))
            send_mail('subject', 'body of the message', 'svc.aacr@taskus.com',
                      ['venkat.gali@taskus.com'])

            return render(request, 'mvp/data.html', {'posts': posts})
        else:
            paginator = Paginator(all_objects, 5)
            page = request.GET.get('page')
            posts = paginator.get_page(page)
            print(Sheets_Update("s"))
            send_mail('subject', 'body of the message', 'svc.aacr@taskus.com',
                      ['venkat.gali@taskus.com'])

            return render(request, 'mvp/success_data.html', {'posts': posts})
    except IndexError:
        paginator = Paginator(all_objects, 5)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        print(Sheets_Update("s"))
        send_mail('subject', 'body of the message', 'svc.aacr@taskus.com',
                  ['venkat.gali@taskus.com'])

        return render(request, 'mvp/data.html', {'posts': posts})


    paginator = Paginator(all_objects, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    print(Sheets_Update("s"))
    send_mail('subject', 'body of the message', 'svc.aacr@taskus.com',
              ['venkat.gali@taskus.com'])

    return render(request, 'mvp/data.html', {'posts': posts})


def single_user(request, mvp_id, req):
    global MESSAGE
    if req == "OverTime":
        if request.method == 'POST':  # and OverTimeUserRequestForm(request.POST).is_valid():
            if OverTimeUserRequestForm(request.POST).is_valid():

                # print("IN HERE!!!")
                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()
                form.for_Name()

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    form = OverTimeUserRequestForm()

                    context = {}
                    context['form'] = form
                    return render(request, "mvp/single.html", context)
                else:
                    mvp_model = form.save()
                    print('mvp_id is :'+ str(MvpUserRequest.objects.latest('id').id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(Status='WFM-IRA-SOT-' + str(mvp_id))

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
                              MESSAGE.replace("Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              ['venkat.gali@taskus.com'])
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
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    mvp_model = form.save()
                    print('mvp_id is :' + str(MvpUserRequest.objects.latest('id').id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-STEL-' + str(mvp_id))
                    context = {'user_ID': 'WFM-IRA-STEL-' + str(mvp_id)}
                    send_mail('WFM - Plotting website submissions: ',
                              MESSAGE.replace("Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              ['venkat.gali@taskus.com'])
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

                    return render(request, "mvp/multi.html", context)

                #################


            elif '_submit' in request.POST:

                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()

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
                    send_mail('WFM - Plotting website submissions: ', MESSAGE.replace("Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              ['venkat.gali@taskus.com'])

                    for mess in mess_split:
                        messages.success(request, mess)
                    context = {'user_ID': 'WFM-IRA-MOT-' + str(mvp_id)}
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
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)
                else:
                    mvp_model = form.save()
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MTEL-S' + str(mvp_id))

                    context = {}

                    new_form = TeleOptiUserRequestForm()
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
                        form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)

                    return render(request, "mvp/multi.html", context)
                else:
                    mvp_model = form.save()
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MTEL-E' + str(mvp_id))
                    context = {}

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
                    context = {'user_ID': 'WFM-IRA-MTEL-' + str(mvp_id)}
                    send_mail('WFM - Plotting website submissions: ',
                              MESSAGE.replace("Enter the values in the portal below", ""), 'svc.aacr@taskus.com',
                              ['venkat.gali@taskus.com'])

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


class MvpViewSet(viewsets.ModelViewSet):
    queryset = MvpUserRequest.objects.all().order_by('-id')[:3]
    # last_ten_in_ascending_order = reversed(last_ten)
    # queryset = MvpUserRequest.objects.reverse()[:2]
    serializer_class = MvpSerializer
