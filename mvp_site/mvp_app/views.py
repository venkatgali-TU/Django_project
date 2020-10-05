from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from .forms import MvpForm, TeleOptiUserRequestForm, OverTimeUserRequestForm
from .models import Mvp
import argparse
import json
import requests
import simplejson as json

CRITICAL = 50
MESSAGE = "Enter the values in the portal below"


def hello_mvp(request):
    # if this is a POST request we need to process the form data

    print(MvpForm(request.POST).errors)
    if request.method == 'POST' and MvpForm(request.POST).is_valid():
        # create a form instance and populate it with data from the request:
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
            username = "Hi " + request.user.username
        else:
            username = "Please login to continue"

        if not MvpForm(request.POST).is_valid():
            if "This field is required." in str(MvpForm(request.POST).errors):
                if "Please" not in username:
                    final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/"+"3054204"#username[5:]#3054204"
                    final_headers = {
                        "x-api-key": "lsUfB4oaUX"
                    }
                    try:
                        #fin = requests.get(final_url, final_headers, False)
                        fin = requests.get(final_url, headers=final_headers, verify=False)
                    except ConnectionError:
                        print("connection refused")

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
                else:
                    messages.warning(request, username)

            else:
                messages.warning(request, str(MvpForm(request.POST).errors))
            form = MvpForm()
            context = {}
            context['form'] = form
            return render(request, "mvp/home.html", context)

        form = MvpForm()
        context = {}
        context['form'] = form
        Mvp.objects.filter(emp_ID=request.user.username).update(emp_ID=username)
        return render(request, "mvp/home.html", context)

    # return HttpResponse("Hi from MVP app!")


def single_user(request, mvp_id, req):
    if req == "OverTime":
        if request.method == 'POST' and OverTimeUserRequestForm(request.POST).is_valid():
            print("IN HERE!!!")
            form = OverTimeUserRequestForm(request.POST)
            # check whether it's valid:
            form.full_clean()
            mvp_model = form.save()
            context = {}
            return render(request, "mvp/thanks.html", context)
        else:
            if not OverTimeUserRequestForm(request.POST).is_valid():
                if "This field is required." in str(OverTimeUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(OverTimeUserRequestForm(request.POST).errors), fail_silently=True)
                form = OverTimeUserRequestForm()
                context = {}
                context['form'] = form
                return render(request, "mvp/single.html", context)

            mvp_model = Mvp.objects.get(id=mvp_id)
            form = OverTimeUserRequestForm()
            context = {}
            context['form'] = form

            return render(request, "mvp/single.html", context)
    else:
        if request.method == 'POST' and TeleOptiUserRequestForm(request.POST).is_valid():
            print("IN HERE!!!")
            form = TeleOptiUserRequestForm(request.POST)
            # check whether it's valid:
            form.full_clean()
            mvp_model = form.save()
            context = {}
            return render(request, "mvp/thanks.html", context)
        else:
            if not TeleOptiUserRequestForm(request.POST).is_valid():
                if "This field is required." in str(TeleOptiUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(TeleOptiUserRequestForm(request.POST).errors), fail_silently=True)
                form = TeleOptiUserRequestForm()
                context = {}
                context['form'] = form
                return render(request, "mvp/single.html", context)

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
                mvp_model = form.save()
                context = {}

                new_form = OverTimeUserRequestForm()
                context['form'] = new_form
                MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                    form.cleaned_data['user_ID']) + " Name : " + str(
                    form.cleaned_data['Name']) + " Start Date : " + str(
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
            elif '_submit' in request.POST:

                form = OverTimeUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                mvp_model = form.save()
                context = {}
                MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                    form.cleaned_data['user_ID']) + " Name : " + str(
                    form.cleaned_data['Name']) + " Start Date : " + str(
                    form.cleaned_data['Start_Date']) + " Start time : " + str(
                    form.cleaned_data['Start_Time']) + " End Date : " + str(
                    form.cleaned_data['End_Date']) + " End Time : " + str(
                    form.cleaned_data['End_Time']) + " Activity : " + str(
                    form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                    form.cleaned_data['Mul_Over'])
                mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                for mess in mess_split:
                    messages.success(request, mess)
                # messages.success(request, MESSAGE.replace("Enter the values in the portal below", ""))
                return render(request, "mvp/thanks.html", context)
        else:
            if not OverTimeUserRequestForm(request.POST).is_valid():
                if "This field is required." in str(OverTimeUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(OverTimeUserRequestForm(request.POST).errors), fail_silently=True)
                form = OverTimeUserRequestForm()
                context = {}
                context['form'] = form
                return render(request, "mvp/multi.html", context)

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
                mvp_model = form.save()
                context = {}

                new_form = TeleOptiUserRequestForm()
                context['form'] = new_form
                MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                    form.cleaned_data['user_ID']) + " Name : " + str(
                    form.cleaned_data['Name']) + " Start Date : " + str(
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
            elif '_submit' in request.POST:
                form = TeleOptiUserRequestForm(request.POST)
                # check whether it's valid:
                form.full_clean()
                mvp_model = form.save()
                context = {}
                MESSAGE = MESSAGE + "\n" + "\n" + " ---- " + "User ID : " + str(
                    form.cleaned_data['user_ID']) + " Name : " + str(
                    form.cleaned_data['Name']) + " Start Date : " + str(
                    form.cleaned_data['Start_Date']) + " Start time : " + str(
                    form.cleaned_data['Start_Time']) + " End Date : " + str(
                    form.cleaned_data['End_Date']) + " End Time : " + str(
                    form.cleaned_data['End_Time']) + " Activity : " + str(
                    form.cleaned_data['Activity']) + " Multiplicator/OverLap : " + str(
                    form.cleaned_data['Mul_Over'])
                mess_split = MESSAGE.replace("Enter the values in the portal below", "").split(" ---- ")
                for mess in mess_split:
                    messages.success(request, mess)

                return render(request, "mvp/thanks.html", context)
        else:
            if not TeleOptiUserRequestForm(request.POST).is_valid():
                if "This field is required." in str(TeleOptiUserRequestForm(request.POST).errors):
                    messages.warning(request, "Please fill all the below fields", fail_silently=True)
                else:
                    messages.warning(request, str(TeleOptiUserRequestForm(request.POST).errors), fail_silently=True)
                form = TeleOptiUserRequestForm()
                context = {}
                context['form'] = form
                return render(request, "mvp/multi.html", context)

            mvp_model = Mvp.objects.get(id=mvp_id)
            form = TeleOptiUserRequestForm()
            context = {}
            context['form'] = form
            messages.info(request, MESSAGE, fail_silently=True)
            return render(request, "mvp/multi.html", context)
