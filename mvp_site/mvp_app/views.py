from datetime import datetime, timedelta

import urllib3
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from rest_framework import generics, mixins
from django.core.mail import EmailMessage

# Create your views here.
from .forms import MvpForm, TeleOptiUserRequestForm, OverTimeUserRequestForm
from .models import Mvp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import csv, io
from django.shortcuts import render
from django.contrib import messages
from .serializers import *

CRITICAL = 50
MESSAGE = "Enter the values in the portal below"
EMAIL = ""
NAME = ""
POSITION = ""
LOCATION = ""

def hello_mvp(request):
    # if this is a POST request we need to process the form data

    global EMAIL, NAME, POSITION, LOCATION

    # print(MvpForm(request.POST).errors)
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
        # print(form.clean_req_type())
        if 'Single' in form.clean_user_req():

            if form.clean_req_type() == "OverTime":
                if POSITION != "Teammate":
                    print(POSITION)
                    return HttpResponseRedirect('/single/' + str(mvp_model.id) + '/OverTime')
                else:
                    context = {}
                    context['form'] = form
                    messages.warning(request,
                                     " You are not authorized to raise requests. Please contact your supervisor!")
                    return render(request, "mvp/home.html", context)

            else:
                if POSITION != "Teammate":
                    print(POSITION)
                    return HttpResponseRedirect('/single/' + str(mvp_model.id) + '/TeleOpti')
                else:
                    context = {}
                    context['form'] = form
                    messages.warning(request,
                                     " You are not authorized to raise requests. Please contact your supervisor!")
                    return render(request, "mvp/home.html", context)
        else:
            # context = {}
            if form.clean_req_type() == "OverTime":
                if POSITION != "Teammate":
                    return HttpResponseRedirect('/multi/' + str(mvp_model.id) + '/OverTime')
                else:
                    context = {}
                    context['form'] = form
                    messages.warning(request,
                                     " You are not authorized to raise requests. Please contact your supervisor!")
                    return render(request, "mvp/home.html", context)
            else:
                if POSITION != "Teammate":
                    return HttpResponseRedirect('/multi/' + str(mvp_model.id) + '/TeleOpti')
                else:
                    context = {}
                    context['form'] = form
                    messages.warning(request,
                                     " You are not authorized to raise requests. Please contact your supervisor!")
                    return render(request, "mvp/home.html", context)

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
                        # #print(username[5:])
                        fin = requests.get(final_url, headers=final_headers, verify=False)

                        # temp_data_json = json.loads(json.dumps(fin.json()))

                        temp_data_json = json.loads(json.dumps(fin.json()))
                        EMAIL = str(temp_data_json['email'])
                        POSITION = str(temp_data_json['position']['name'])
                        NAME = str(temp_data_json['firstName']) + " " + str(temp_data_json['lastName'])
                        LOCATION = str(temp_data_json['site']['location'])
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
                        # print("connection refused")

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
    try:
        locations = {}
        with open(r'C:\Users\vg3054204\Desktop\roster_location.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1:
                    locations[row[0]] = row[1]
    except:
        locations[row[0]] = ""
    try:
        timezone = ""
        with open(r'C:\Users\vg3054204\Desktop\roster_timezone.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 0 and row[0] != '' and row[1] != '' and str(row[0]).lower() == str(request.user.email).lower():
                    timezone = row[1]
                    if timezone == 'Central Standard Time':
                        timezone = 'US/Central'
                    elif timezone =='Singapore Standard Time':
                        timezone = 'Asia/Singapore'
                    elif timezone == 'Eastern Standard Time':
                        timezone = 'US/Eastern'
                    elif timezone == 'GTB Standard Time':
                        timezone = 'Etc/GMT'
                    elif timezone =='India Standard Time':
                        timezone = 'Asia/Kolkata'
                    elif timezone == 'Pacific Standard Time':
                        timezone = 'US/Pacific'
                    elif timezone =='Taipei Standard Time':
                        timezone = 'Asia/Taipei'
                    else:
                        timezone = 'US/Pacific'
                    break
    except:
        pass
    # print(locations)
    if timezone == '':
        print('here')
        timezone = 'US/Pacific'

    if request.method == "POST":
        print("--")
        print(request.POST)
        s_d = request.POST['trip-start']
        e_d = request.POST['trip-end']
        ind = 0
        ph = 0
        us = 0
        count = 0
        for item in MvpUserRequest.objects.all().filter(created_at__range=[s_d, e_d]).values_list('user_ID', flat=True):
            if item in locations:
                if locations[item] == "PH":
                    ph = ph + 1
                elif locations[item] == "US":
                    us = us + 1
                elif locations[item] == "IND":
                    ind = ind + 1
            else:
                count = count + 1
        total = len(MvpUserRequest.objects.all().filter(created_at__range=[s_d, e_d]))
        InProgress = len(MvpUserRequest.objects.all().exclude(Status__contains='Complete').exclude(
            Status__contains='Help Needed').filter(created_at__range=[s_d, e_d]))
        Completed = len(
            MvpUserRequest.objects.all().filter(Status__contains='Complete').filter(created_at__range=[s_d, e_d]))
        HelpNeeded = len(
            MvpUserRequest.objects.all().filter(Status__contains='Help Needed').filter(created_at__range=[s_d, e_d]))
        Failed = len(
            MvpUserRequest.objects.all().filter(Status__contains='Failed').filter(created_at__range=[s_d, e_d]))
        key = request.POST['key']
        name_ = request.POST['name']
        camp = request.POST['camp']
        if key == '':
            if name_ =='':
                all_objects = MvpUserRequest.objects.all().filter(Timezone__contains=camp).filter(
                    created_at__range=[s_d, e_d]).order_by('-id')
            elif camp== '':
                all_objects = MvpUserRequest.objects.all().filter(
                    BreakTime__contains=name_).filter(
                    created_at__range=[s_d, e_d]).order_by('-id')
        elif name_ == '':
            if key == '':
                all_objects = MvpUserRequest.objects.all().filter(Timezone__contains=camp).filter(
                    created_at__range=[s_d, e_d]).order_by('-id')
            elif camp == '':
                all_objects = MvpUserRequest.objects.all().filter(Name__contains=key).filter(
                    created_at__range=[s_d, e_d]).order_by('-id')

        elif camp == '':
            if name_=='':
                all_objects = MvpUserRequest.objects.all().filter(Name__contains=key).filter(
                    created_at__range=[s_d, e_d]).order_by('-id')
            elif key == '':
                all_objects = MvpUserRequest.objects.all().filter(
                    BreakTime__contains=name_).filter(
                    created_at__range=[s_d, e_d]).order_by('-id')
        elif camp == name_ == key == '':
            all_objects = MvpUserRequest.objects.all().filter(
                created_at__range=[s_d, e_d]).order_by('-id')
        elif camp != '' and name_ != '' and key != '':
            all_objects = MvpUserRequest.objects.all().filter(Name__contains=key).filter(
                BreakTime__contains=name_).filter(Timezone__contains=camp).filter(
                created_at__range=[s_d, e_d]).order_by('-id')

        paginator = Paginator(all_objects, 1000)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        return render(request, 'mvp/confirmation.html',
                      {'posts': posts, 'total': total, 'inprogress': InProgress, 'completed': Completed,
                       'helpneeded': HelpNeeded, 'failed': Failed, 'us': us, 'ind': ind, 'ph': ph, 'st_d': s_d,
                       'end_date': e_d,'my_timezone':timezone})
    elif request.method == 'GET':
        all_objects = MvpUserRequest.objects.all().order_by('-id')
        s_d = "2020-10-26"
        now = datetime.now()
        e_d = str(now).split(' ')[0]
        ind = 0
        ph = 0
        us = 0
        count = 0
        for item in MvpUserRequest.objects.all().values_list('user_ID', flat=True):
            if item in locations:
                if locations[item] == "PH":
                    ph = ph + 1
                elif locations[item] == "US":
                    us = us + 1
                elif locations[item] == "IND":
                    ind = ind + 1
            else:
                count = count + 1

        total = len(MvpUserRequest.objects.all())
        InProgress = len(MvpUserRequest.objects.all().exclude(Status__contains='Complete').exclude(
            Status__contains='Help Needed'))
        Completed = len(
            MvpUserRequest.objects.all().filter(Status__contains='Complete'))
        HelpNeeded = len(
            MvpUserRequest.objects.all().filter(Status__contains='Help Needed'))
        Failed = len(
            MvpUserRequest.objects.all().filter(Status__contains='Failed'))

        # print(" success data : " + request.POST['key'])

        all_objects = MvpUserRequest.objects.all().order_by('-id')
        paginator = Paginator(all_objects, 200)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        return render(request, 'mvp/confirmation.html',
                      {'posts': posts, 'total': total, 'inprogress': InProgress, 'completed': Completed,
                       'helpneeded': HelpNeeded, 'failed': Failed, 'us': us, 'ind': ind, 'ph': ph, 'st_d': s_d,
                       'end_date': e_d,'my_timezone':timezone})

def help_needed(request):
    try:
        locations = {}
        with open(r'C:\Users\vg3054204\Desktop\roster_location.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1:
                    locations[row[0]] = row[1]
    except:
        locations[row[0]] = ""
    # print(locations)

    if request.method == "POST":

        ids = ""
        for items in request.POST:
            if "chex" in items:
                MvpUserRequest.objects.filter(id=items.split("_")[1].split('$')[0]).update(
                    Status='Complete')
                ids = ids + items.split("_")[1].split('$')[1]
        all_objects = MvpUserRequest.objects.all().filter(Status__contains='elp Needed').order_by('-id')
        paginator = Paginator(all_objects, 100)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        html_str = "<h1>Thanks for your submission</h1><p>You have completed the folowing request IDs, Please check in submissions page for more info.</p><p><b>" + ids + "</b></p>"
        msg = EmailMessage('WFM - Plotting website submissions: ', html_str, 'svc.aacr@taskus.com',
                           [request.user.email, 'venkat.gali@taskus.com'])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        return render(request, 'mvp/help_needed.html',
                      {'posts': posts})
    elif request.method == 'GET':
        print("--")
        print(request.POST)

        all_objects = MvpUserRequest.objects.all().filter(Status__contains='elp Needed').order_by('-id')
        paginator = Paginator(all_objects, 100)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        return render(request, 'mvp/help_needed.html',
                      {'posts': posts})

def failed(request):
    try:
        locations = {}
        with open(r'C:\Users\vg3054204\Desktop\roster_location.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1:
                    locations[row[0]] = row[1]
    except:
        locations[row[0]] = ""
    # print(locations)

    if request.method == "POST":

        ids = ""
        for items in request.POST:
            if "chex" in items:
                MvpUserRequest.objects.filter(id=items.split("_")[1].split('$')[0]).update(
                    Status='Complete')
                ids = ids + items.split("_")[1].split('$')[1]
        all_objects = MvpUserRequest.objects.all().filter(Status__contains='Failed').order_by('-id')
        paginator = Paginator(all_objects, 100)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        html_str = "<h1>Thanks for your submission</h1><p>You have completed the folowing request IDs, Please check in submissions page for more info.</p><p><b>" + ids + "</b></p>"
        msg = EmailMessage('WFM - Plotting website submissions: ', html_str, 'svc.aacr@taskus.com',
                           [request.user.email, 'venkat.gali@taskus.com'])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        return render(request, 'mvp/help_needed.html',
                      {'posts': posts})
    elif request.method == 'GET':
        print("--")
        print(request.POST)

        all_objects = MvpUserRequest.objects.all().filter(Status__contains='Failed').order_by('-id')
        paginator = Paginator(all_objects, 100)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        return render(request, 'mvp/help_needed.html',
                      {'posts': posts})

def single_user(request, mvp_id, req):
    global MESSAGE
    # #print("req is :" + req)
    NAME = request.user.first_name + " " + request.user.last_name
    if req == "OverTime":
        if request.method == 'POST':  # and OverTimeUserRequestForm(request.POST).is_valid():
            if OverTimeUserRequestForm(request.POST).is_valid():

                # #print("IN HERE!!!")
                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                form.clean()
                form.for_Name()
                breaktime = form.for_break()
                # #print("breaktime" + breaktime)

                if "Please" in form.clean_user_number():
                    messages.warning(request, "Please enter a valid employee number", fail_silently=True)
                    form = OverTimeUserRequestForm()

                    context = {}
                    context['form'] = form
                    return render(request, "mvp/single.html", context)
                else:
                    mvp_model = form.save()
                    try:
                        campaigns = {}
                        with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) > 1:
                                    campaigns[row[0]] = row[1]
                    except:
                        context = {'user_ID' : 'Cannot find the right campaign for the User, Please check with digital@taskus.com'}
                    camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Timezone=camp)
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-SOT-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=NAME)


                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "$User ID : " + str(
                        form.cleaned_data['user_ID']) + " $Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " $Start time : " + str(
                        form.cleaned_data['Start_Time']) + " $End Date : " + str(
                        form.cleaned_data['End_Date']) + " $End Time : " + str(
                        form.cleaned_data['End_Time']) + " $Activity : " + str(
                        form.cleaned_data['Activity']) + " $Multiplicator/OverLap : " + str(
                        form.cleaned_data['Mul_Over'])
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    context = {'user_ID': 'WFM-IRA-SOT-' + str(mvp_id)}
                    if "Ind" in LOCATION:
                        data_dict = {"Request_ID": ['WFM-IRA-SOT-' + str(mvp_id)], "User_ID": [str(
                        form.cleaned_data['user_ID'])], "Start_Date": [str(
                        form.cleaned_data['Start_Date'])], "Start_Time": [str(
                        form.cleaned_data['Start_Time'])],
                                     "End_Date": [str(
                        form.cleaned_data['End_Date'])],
                                     "End_Time": [str(
                        form.cleaned_data['End_Time'])], "Activity": [str(
                        form.cleaned_data['Activity'])], "Mul_Overlap": [str(
                        form.cleaned_data['Mul_Over'])], }
                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com','workforce.indore@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()
                    else:
                        data_dict = {"Request_ID": ['WFM-IRA-SOT-' + str(mvp_id)], "User_ID": [str(
                            form.cleaned_data['user_ID'])], "Start_Date": [str(
                            form.cleaned_data['Start_Date'])], "Start_Time": [str(
                            form.cleaned_data['Start_Time'])],
                                     "End_Date": [str(
                                         form.cleaned_data['End_Date'])],
                                     "End_Time": [str(
                                         form.cleaned_data['End_Time'])], "Activity": [str(
                                form.cleaned_data['Activity'])], "Mul_Overlap": [str(
                                form.cleaned_data['Mul_Over'])], }

                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()

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
                # print("IN HERE!!!")
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
                    MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "$User ID : " + str(
                        form.cleaned_data['user_ID']) + " $Start Date : " + str(
                        form.cleaned_data['Start_Date']) + " $Start time : " + str(
                        form.cleaned_data['Start_Time']) + " $End Date : " + str(
                        form.cleaned_data['End_Date']) + " $End Time : " + str(
                        form.cleaned_data['End_Time']) + " $Activity : " + str(
                        form.cleaned_data['Activity']) + " $Multiplicator/OverLap : "
                    mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                    for mess in mess_split:
                        messages.success(request, mess)
                    mvp_model = form.save()
                    try:
                        campaigns = {}
                        with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) > 1:
                                    campaigns[row[0]] = row[1]
                    except:
                        context = {
                            'user_ID': 'Cannot find the right campaign for the User, Please check with digital@taskus.com'}
                    camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Timezone=camp)
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-STEL-' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=NAME)
                    context = {'user_ID': 'WFM-IRA-STEL-' + str(mvp_id)}
                    if "Ind" in LOCATION:
                        data_dict = {"Request_ID": ['WFM-IRA-STEL-' + str(mvp_id)], "User_ID": [str(
                            form.cleaned_data['user_ID'])], "Start_Date": [str(
                            form.cleaned_data['Start_Date'])], "Start_Time": [str(
                            form.cleaned_data['Start_Time'])],
                                     "End_Date": [str(
                                         form.cleaned_data['End_Date'])],
                                     "End_Time": [str(
                                         form.cleaned_data['End_Time'])], "Activity": [str(
                                form.cleaned_data['Activity'])], "Mul_Overlap": "" }
                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com',
                                            'workforce.indore@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()
                    else:
                        data_dict = {"Request_ID": ['WFM-IRA-STEL-' + str(mvp_id)], "User_ID": [str(
                            form.cleaned_data['user_ID'])], "Start_Date": [str(
                            form.cleaned_data['Start_Date'])], "Start_Time": [str(
                            form.cleaned_data['Start_Time'])],
                                     "End_Date": [str(
                                         form.cleaned_data['End_Date'])],
                                     "End_Time": [str(
                                         form.cleaned_data['End_Time'])], "Activity": [str(
                                form.cleaned_data['Activity'])], "Mul_Overlap": [''], }
                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()

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
    NAME = request.user.first_name + " " + request.user.last_name
    if req == "OverTime":
        if request.method == 'POST' and OverTimeUserRequestForm(request.POST).is_valid():
            data_dict = {"Request_ID": [], "User_ID": [], "Start_Date": [], "Start_Time": [],
                         "End_Date": [],
                         "End_Time": [], "Activity": [], "Mul_Overlap": [], }
            if '_con' in request.POST:
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
                    context = {}
                    try:
                        campaigns = {}
                        with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) > 1:
                                    campaigns[row[0]] = row[1]
                    except:
                        context = {
                            'user_ID': 'Cannot find the right campaign for the User, Please check with digital@taskus.com'}
                    camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Timezone=camp)
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MOT-S-' + str(mvp_id))


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
                        BreakTime=NAME)
                    temp_list = data_dict['Request_ID']
                    temp_list.append('WFM-IRA-MOT-S-' + str(mvp_id))
                    data_dict['Request_ID'] = temp_list
                    temp_list = data_dict['User_ID']
                    temp_list.append(str(
                        form.cleaned_data['user_ID']))
                    data_dict['User_ID'] = temp_list
                    temp_list = data_dict['Start_Date']
                    temp_list.append(str(
                        form.cleaned_data['Start_Date']))
                    data_dict['Start_Date'] = temp_list
                    temp_list = data_dict['Start_Time']
                    temp_list.append(str(
                        form.cleaned_data['Start_Time']))
                    data_dict['Start_Time'] = temp_list
                    temp_list = data_dict['End_Date']
                    temp_list.append(str(
                        form.cleaned_data['End_Date']))
                    data_dict['End_Date'] = temp_list
                    temp_list = data_dict['End_Time']
                    temp_list.append(str(
                        form.cleaned_data['End_Time']))
                    data_dict['End_Time'] = temp_list
                    temp_list = data_dict['Activity']
                    temp_list.append(str(
                        form.cleaned_data['Activity']))
                    data_dict['Activity'] = temp_list
                    temp_list = data_dict['Mul_Overlap']
                    temp_list.append(str(
                        form.cleaned_data['Mul_Over']))
                    data_dict['Mul_Overlap'] = temp_list

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
                    try:
                        campaigns = {}
                        with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) > 1:
                                    campaigns[row[0]] = row[1]
                        camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    except:
                        camp = 'Cannot find the right campaign for the User, Please check with digital@taskus.com'
                        context = {
                            'user_ID': 'Cannot find the right campaign for the User, Please check with digital@taskus.com'}

                    #camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Timezone=camp)


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
                        Name='WFM-IRA-MOT-E' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=NAME)
                    temp_list = data_dict['Request_ID']
                    temp_list.append('WFM-IRA-MOT-E' + str(mvp_id))
                    data_dict['Request_ID'] = temp_list
                    temp_list = data_dict['User_ID']
                    temp_list.append(str(
                        form.cleaned_data['user_ID']))
                    data_dict['User_ID'] = temp_list
                    temp_list = data_dict['Start_Date']
                    temp_list.append(str(
                        form.cleaned_data['Start_Date']))
                    data_dict['Start_Date'] = temp_list
                    temp_list = data_dict['Start_Time']
                    temp_list.append(str(
                        form.cleaned_data['Start_Time']))
                    data_dict['Start_Time'] = temp_list
                    temp_list = data_dict['End_Date']
                    temp_list.append(str(
                        form.cleaned_data['End_Date']))
                    data_dict['End_Date'] = temp_list
                    temp_list = data_dict['End_Time']
                    temp_list.append(str(
                        form.cleaned_data['End_Time']))
                    data_dict['End_Time'] = temp_list
                    temp_list = data_dict['Activity']
                    temp_list.append(str(
                        form.cleaned_data['Activity']))
                    data_dict['Activity'] = temp_list
                    temp_list = data_dict['Mul_Overlap']
                    temp_list.append(str(
                        form.cleaned_data['Mul_Over']))
                    data_dict['Mul_Overlap'] = temp_list
                    if "Ind" in LOCATION:

                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com',
                                            'workforce.indore@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()

                    else:
                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()


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
            data_dict = {"Request_ID": [], "User_ID": [], "Start_Date": [], "Start_Time": [],
                         "End_Date": [],
                         "End_Time": [], "Activity": [], "Mul_Overlap": [], }

            if '_con' in request.POST:
                # print("IN HERE!!!")
                # print(request.POST)
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
                    try:
                        campaigns = {}
                        with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) > 1:
                                    campaigns[row[0]] = row[1]
                    except:
                        context = {
                            'user_ID': 'Cannot find the right campaign for the User, Please check with digital@taskus.com'}
                    camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Timezone=camp)
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MTEL-S' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-MTEL-S' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=NAME)

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
                    temp_list = data_dict['Request_ID']
                    temp_list.append('WFM-IRA-MTEL-S' + str(mvp_id))
                    data_dict['Request_ID'] = temp_list
                    temp_list = data_dict['User_ID']
                    temp_list.append(str(
                        form.cleaned_data['user_ID']))
                    data_dict['User_ID'] = temp_list
                    temp_list = data_dict['Start_Date']
                    temp_list.append(str(
                        form.cleaned_data['Start_Date']))
                    data_dict['Start_Date'] = temp_list
                    temp_list = data_dict['Start_Time']
                    temp_list.append(str(
                        form.cleaned_data['Start_Time']))
                    data_dict['Start_Time'] = temp_list
                    temp_list = data_dict['End_Date']
                    temp_list.append(str(
                        form.cleaned_data['End_Date']))
                    data_dict['End_Date'] = temp_list
                    temp_list = data_dict['End_Time']
                    temp_list.append(str(
                        form.cleaned_data['End_Time']))
                    data_dict['End_Time'] = temp_list
                    temp_list = data_dict['Activity']
                    temp_list.append(str(
                        form.cleaned_data['Activity']))
                    data_dict['Activity'] = temp_list
                    temp_list = data_dict['Mul_Overlap']
                    temp_list.append('')
                    data_dict['Mul_Overlap'] = temp_list
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
                    try:
                        campaigns = {}
                        with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) > 1:
                                    campaigns[row[0]] = row[1]
                    except:
                        context = {
                            'user_ID': 'Cannot find the right campaign for the User, Please check with digital@taskus.com'}
                    camp = campaigns[MvpUserRequest.objects.latest('id').user_ID]
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Timezone=camp)
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Status='WFM-IRA-MTEL-E' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        Name='WFM-IRA-MTEL-E' + str(mvp_id))
                    MvpUserRequest.objects.filter(id=MvpUserRequest.objects.latest('id').id).update(
                        BreakTime=NAME)
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
                    temp_list = data_dict['Request_ID']
                    temp_list.append('WFM-IRA-MTEL-' + str(mvp_id))
                    data_dict['Request_ID'] = temp_list
                    temp_list = data_dict['User_ID']
                    temp_list.append(str(
                        form.cleaned_data['user_ID']))
                    data_dict['User_ID'] = temp_list
                    temp_list = data_dict['Start_Date']
                    temp_list.append(str(
                        form.cleaned_data['Start_Date']))
                    data_dict['Start_Date'] = temp_list
                    temp_list = data_dict['Start_Time']
                    temp_list.append(str(
                        form.cleaned_data['Start_Time']))
                    data_dict['Start_Time'] = temp_list
                    temp_list = data_dict['End_Date']
                    temp_list.append(str(
                        form.cleaned_data['End_Date']))
                    data_dict['End_Date'] = temp_list
                    temp_list = data_dict['End_Time']
                    temp_list.append(str(
                        form.cleaned_data['End_Time']))
                    data_dict['End_Time'] = temp_list
                    temp_list = data_dict['Activity']
                    temp_list.append(str(
                        form.cleaned_data['Activity']))
                    data_dict['Activity'] = temp_list
                    temp_list = data_dict['Mul_Overlap']
                    temp_list.append('')
                    data_dict['Mul_Overlap'] = temp_list
                    #(prod_venv) C:\Users\vg3054204\PycharmProjects\Django_project\mvp_site>python manage.py runserver 0.0.0.0:80

                    if "Ind" in LOCATION:
                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com',
                                            'workforce.indore@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()
                    else:
                        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
                            data_dict.keys()) + '</th></tr>'
                        for row in zip(*data_dict.values()):
                            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

                        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'
                        msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                                           [request.user.email, 'venkat.gali@taskus.com',
                                            'workforce.indore@taskus.com'])
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()

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
    # print("name is: " + request.user.email)
    NAME = request.user.first_name + " " + request.user.last_name
    print("name is: " + NAME)

    template = "mvp/profile_upload.html"
    data = MvpUserRequest.objects.all().order_by('-id')[0:1000]
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
        submitted_requests = {}
        try:
            campaigns = {}
            with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > 1:
                        campaigns[row[0]] = row[1]
        except:
            prompt['order'] = "Cannot find a campaign for the user!"

        with open(
                'C:/Users/vg3054204/PycharmProjects/Django_project/mvp_site/mvp_app/static/mvp_app/submission_results.csv',
                'w', newline="") as csvfile:
            new_header = ['Req_ID', 'User_ID', 'Start_Date',
                          'Start_Time',
                          'End_Date',
                          'End_Time', 'Activity', 'Mul/Overlap', 'Status'
                          ]
            csvwriter = csv.DictWriter(csvfile, fieldnames=new_header)
            csvwriter.writeheader()
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                count = count + 1
                req_id = MvpUserRequest.objects.latest('id').id
                request_ID_str = ""

                try:
                    if count != 1 and count < 500:
                        str_time = column[3]
                        end_time = column[4]
                        str_date = column[1]
                        end_date = column[2]
                        start_time_date = datetime.strptime(str_time, '%H:%M')
                        end_time_date = datetime.strptime(end_time, '%H:%M')
                        str_date = datetime.strptime(str_date, '%Y-%m-%d')
                        end_date = datetime.strptime(end_date, '%Y-%m-%d')
                        past = datetime.now() - timedelta(days=7)
                        if column[0] in campaigns and end_date >= str_date >= past:
                            if start_time_date > end_time_date and str_date == end_date:
                                continue
                            timezone = campaigns[column[0]]
                            if len(column) <= 6:
                                request_ID_str = "WFM-IRA-MTEL-" + str(req_id)
                                submitted_requests[request_ID_str] = column[0] + "!" + column[1] + "!" + column[
                                    2] + "!" + \
                                                                     column[3] + "!" + column[4] + "!" + column[5] + "!"
                                _, created = MvpUserRequest.objects.update_or_create(
                                    user_ID=column[0],
                                    Name=request_ID_str,
                                    Start_Date=column[1],
                                    End_Date=column[2],
                                    Start_Time=column[3],
                                    End_Time=column[4],
                                    Activity=column[5],
                                    Mul_Over='',
                                    Timezone=timezone,
                                    BreakTime=NAME,
                                    Status='In Progress'
                                )
                                csvwriter.writerow(
                                    {'Req_ID': request_ID_str, 'User_ID': column[0], 'Start_Date': column[1],
                                     'Start_Time': column[3],
                                     'End_Date': column[2],
                                     'End_Time': column[4], 'Activity': column[5], 'Mul/Overlap': "",
                                     'Status': "Success"})
                            else:
                                request_ID_str = "WFM-IRA-MOT-" + str(req_id)
                                submitted_requests[request_ID_str] = column[0] + "!" + column[1] + "!" + column[
                                    2] + "!" + \
                                                                     column[3] + "!" + column[4] + "!" + column[
                                                                         5] + "!" + \
                                                                     column[6]
                                _, created = MvpUserRequest.objects.update_or_create(
                                    user_ID=column[0],
                                    Name=request_ID_str,
                                    Start_Date=column[1],
                                    End_Date=column[2],
                                    Start_Time=column[3],
                                    End_Time=column[4],
                                    Activity=column[5],
                                    Mul_Over=column[6],
                                    Timezone=timezone,
                                    BreakTime=NAME,
                                    Status='In Progress'
                                )
                                csvwriter.writerow(
                                    {'Req_ID': request_ID_str, 'User_ID': column[0], 'Start_Date': column[1],
                                     'Start_Time': column[3],
                                     'End_Date': column[2],
                                     'End_Time': column[4], 'Activity': column[5], 'Mul/Overlap': column[6],
                                     'Status': "Success"})
                            prompt['order'] = "Successfully completed " + str(
                                count - 1) + " records! please check the submissions tasks for status"
                        else:
                            csvwriter.writerow({'Req_ID': request_ID_str, 'User_ID': column[0], 'Start_Date': column[1],
                                                'Start_Time': column[3],
                                                'End_Date': column[2],
                                                'End_Time': column[4], 'Activity': column[5], 'Mul/Overlap': "",
                                                'Status': "Fail"})
                except Exception as e:
                    prompt['order'] = e
                    csvwriter.writerow({'Req_ID': request_ID_str, 'User_ID': column[0], 'Start_Date': column[1],
                                        'Start_Time': column[3],
                                        'End_Date': column[2],
                                        'End_Time': column[4], 'Activity': column[5], 'Mul/Overlap': "",
                                        'Status': "Fail"})

                    pass

        data_dict = {"Request_ID": [], "User_ID": [], "Start_Date": [], "Start_Time": [], "End_Date": [],
                     "End_Time": [], "Activity": [], "Mul_Overlap": [], }
        for item in submitted_requests:
            temp_list = data_dict['Request_ID']
            temp_list.append(item)
            data_dict['Request_ID'] = temp_list

            new_items = submitted_requests[item].split('!')
            temp_list = data_dict['User_ID']
            temp_list.append(new_items[0])
            data_dict['User_ID'] = temp_list
            temp_list = data_dict['Start_Date']
            temp_list.append(new_items[1])
            data_dict['Start_Date'] = temp_list
            temp_list = data_dict['Start_Time']
            temp_list.append(new_items[2])
            data_dict['Start_Time'] = temp_list
            temp_list = data_dict['End_Date']
            temp_list.append(new_items[3])
            data_dict['End_Date'] = temp_list
            temp_list = data_dict['End_Time']
            temp_list.append(new_items[4])
            data_dict['End_Time'] = temp_list
            temp_list = data_dict['Activity']
            temp_list.append(new_items[5])
            data_dict['Activity'] = temp_list
            temp_list = data_dict['Mul_Overlap']
            temp_list.append(new_items[6])
            data_dict['Mul_Overlap'] = temp_list

        html_email = '<h1>Thanks for your submission!</h1><h1>Submissions:</h1><table cellpadding = "0" cellspacing = "0" width = "640" align = "center" border = "1"><tr><th>' + '</th><th>'.join(
            data_dict.keys()) + '</th></tr>'

        for row in zip(*data_dict.values()):
            html_email += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'

        html_email += '</table><h1>Please contact digital team for any assitance, Thanks</h1>'


        EMAIL = request.user.email

        if "Ind" in LOCATION:
            msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                               [EMAIL, "workforce.indore@taskus.com", 'venkat.gali@taskus.com'])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        else:
            msg = EmailMessage('WFM - Plotting website submissions: ', html_email, 'svc.aacr@taskus.com',
                               [EMAIL, 'venkat.gali@taskus.com'])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

        return render(request, template, prompt)
    except Exception as e:

        prompt['order'] = str(e)
        return render(request, template, prompt)

@api_view(['GET', 'POST'])
def request_list(request):
    """
    List all products, or create a new product.
    """
    if request.method == 'GET':
        products = MvpUserRequest.objects.all().exclude(Status__contains='omplete').exclude(
            Status__contains='eeded').order_by('created_at')[:20]  ##Changed from id to createdat
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
            # MvpUserRequest.objects.filter(id=request.data['id']).update(
            #     BreakTime=datetime.now())
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
