from django import forms
from django.core.exceptions import ValidationError
from .models import Mvp, MvpUserRequest
from email.utils import parseaddr
import re
from datetime import datetime, timedelta
import json
import requests
import simplejson as json

USERS_REQ_TYPE = [('single_user', 'Single User'), ('multi_user', 'Multiple Users')]
SITE_NAMES = [('rgz', 'Rangreza'), ('liz_n', 'Lizzys Nook'), ('liz_l', 'LizardBear Lair'), ('htw', 'Home Teamwork'),
              ('fe', 'Fort Excellence'),
              ('liz_lg', 'Lizzys Lagoon'), ('boh', 'Bohol'), ('lh', 'Light House'), ('cha', 'Chateau Ridiculous'),
              ('adv_in', 'Adventure Intelligence'),
              ('chariot', 'Chariot'),
              ('cirrus', 'Cirrus'),
              ('f_lwt', 'Frontier LWT'),

              ('f_chr', 'Frontier CHR'),

              ('galaxis', 'Galaxis'),

              ('h_chr', 'Hybrid CHR'),

              ('ireland', 'Ireland'),

              ('lch', 'Lizzys ClubHouse'),

              ('lwt', 'Lizzys Watch Tower'),

              ('tot', 'TeleOpti Team'),

              ('grid', 'The Grid'),

              ('oasis', 'The Oasis'),

              ('thessaloniki', 'Thessaloniki'),

              ]
CAMPAIGNS = [('bad', 'Badger'),
             ('ddsh', 'DoorDash'), ('lgue', 'League'), ('letgo', 'LetGo'), ('rev', 'Revolut'),
             ('shop', 'Shopify'), ('tind', 'Tinder'), ('blck', 'BLCK'), ('n26', 'N26'), ('goodrx', 'Good-RX'),
             ('mailchimp', 'MailChimp'), ('afterpay', 'AfterPay'), ('philo', 'Philo'), ('betterdoctor', 'BetterDoctor'),
             ('spotify', 'Spotify'), ('storable', 'Storable'), ('missionlane', 'Mission Lane'),
             ('frontierBi', 'Frontier BI'), ('front_off', 'Frontier Offensive Content - Spanish'),
             ('frontier_sales', 'Frontier Sales'), ('frontier_service', 'Frontier Service'),
             ('frontier_civic_divisive', 'Frontier Civic Divisive Content'), ('frontier_ai', 'Frontier AI Integrity'),
             ('bcp', 'BCP'), ('hoteltonight', 'Hotel Night'), ('seatgeek', 'Seat Geek'), ('balsam', 'Balsam Brand'),
             ('squareenix', 'Square Enix'), ('airbnb', 'AirBnb'), ('atom', 'Atom')
             ]
ROLES = [('tl_etl', 'Team Leader of interim Team Leader'), ('sme', 'SME'), ('opm', 'Operation Manager and up'),
         ('sup', 'Support department (Non Operations)')]
BUSINESS_UNITS = [('san', 'San Antonio'), ('tij', 'Tijuana'), ('ind', 'India')]
REQUEST_TYPES = [('ot', 'OverTime'), ('tel', 'TeleOpti plotting')]
OT_TYPES = [('part_ot', 'Partial Over Time'), ('full_ot', 'Full Day OT')]
LOCATIONS = [('nam', 'NAM'), ('mxc', 'Mexico'), ('ind', 'India')]
YEAR_CHOICES = ['2020', '2021', '2022']
OT_ACTIVITY = [('prdtime', 'Productive Time'), ('prdtime_15', 'Productive Time 15 mins'),
               ('prdtime_30mins', 'Productive Time 30 mins'),
               ('email', 'Email'), ('email_30mins', 'Email 30 mins'), ('chat', 'Chat'),
               ('sup_hour', 'Supplementary Hour')]

OT_MULTIPLICATOR = [('ot', 'OverTime'), ('bil_ot', 'Billable OverTime'), ('nonbil_OT', 'Non-Billable OverTime')]
TELEOPTI_ACTIVITY = [('c&d', 'Coaching and Development'), ('daily_su', 'Daily Stand Up'),
                     ('teammeetings', 'Team Meetings'),
                     ('vto', 'Voluntary Time Off'), ('ct', 'Client Training')]
TELEOPTI_OVERLAP = [('move_non', 'Move Non-Overwritable'), ('dont', 'Do Not Make Changes'), ('override', 'Override'),
                    ('keep_non', 'Keep non-overwritable'), ('na', 'N/A - only for VTO Code')]
BREAK = [('15min', '15 mins'), ('lunch_15', 'Lunch + 15 min'), ('lunch_30', 'Lunch + 30 min'),
         ('lunch_45', 'Lunch + 45 min'), ('lunch_60', 'Lunch + 60min'), ('no', 'No Break')]


class MvpForm(forms.ModelForm):
    # emp_ID = forms.CharField(label='Employee ID', required=True, widget=forms.TextInput(
    #     attrs={'placeholder': 'Please give the employee ID of the requesting person'}))
    # emp_Name = forms.CharField(label='Employee Name', required=True, widget=forms.TextInput(
    #     attrs={'placeholder': 'Please give the employee Name of the requesting person'}))
    #
    # supervisor = forms.CharField(label='Supervisor Name', required=True, widget=forms.TextInput(
    #     attrs={'placeholder': 'Please give the Supervisor ID of the requesting person'}))
    # email = forms.CharField(label='Email Address', required=True, widget=forms.TextInput(
    #     attrs={'placeholder': 'Please give the employee email address of the requesting person'}))
    #
    # role = forms.ChoiceField(label='Role', required=True, choices=ROLES)
    # site = forms.ChoiceField(label='Site', required=True, choices=SITE_NAMES)
    # campaign = forms.ChoiceField(label='Campaign', required=True, choices=CAMPAIGNS)
    # business_unit = forms.ChoiceField(label='Business Unit', required=True, choices=BUSINESS_UNITS)
    #
    # location = forms.ChoiceField(label='Location', required=True, choices=LOCATIONS)
    req_type = forms.ChoiceField(label='Request Type', required=True, choices=REQUEST_TYPES)

    user_req = forms.ChoiceField(
        label='User Request Type',
        choices=USERS_REQ_TYPE,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Mvp
        fields = [
            # 'emp_ID',
            # 'emp_Name',
            # 'location',
            'req_type',
            # 'supervisor',
            # 'email',
            # 'role',
            # 'site',
            # 'campaign',
            # 'business_unit',
            'user_req'
        ]

    def clean_emp_ID(self, *args, **kwargs):
        emp_ID = self.cleaned_data.get("emp_ID")
        if len(emp_ID) == 6 and emp_ID.isdecimal():
            return emp_ID
        else:
            raise forms.ValidationError("This is not a valid employee ID")

    def clean_emp_Name(self, *args, **kwargs):
        emp_Name = self.cleaned_data.get("emp_Name")
        return emp_Name

    def clean_location(self, *args, **kwargs):
        location = self.cleaned_data.get("location")
        for items in LOCATIONS:
            if location in items:
                new_location = items[1]
        return new_location

    def clean_req_type(self, *args, **kwargs):
        req_type = self.cleaned_data.get("req_type")
        for items in REQUEST_TYPES:
            if req_type in items:
                new_req_type = items[1]
        return new_req_type

    def clean_user_req(self, *args, **kwargs):
        user_req = self.cleaned_data.get("user_req")
        for items in USERS_REQ_TYPE:
            if user_req in items:
                new_user_req = items[1]
        return new_user_req

    def clean_email(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        if '@taskus.com' in parseaddr(email)[1]:
            return email
        else:
            raise forms.ValidationError("This is not a valid email address")

    def clean_supervisor(self, *args, **kwargs):
        supervisor = self.cleaned_data.get("supervisor")
        if any(i.isdigit() for i in supervisor):
            raise forms.ValidationError("Not a valid supervisor")
        else:
            return supervisor

    def clean_campaign(self, *args, **kwargs):
        campaign = self.cleaned_data.get("campaign")
        for items in CAMPAIGNS:
            if campaign in items:
                new_campaign = items[1]
        return new_campaign

    def clean_business_unit(self, *args, **kwargs):
        business_unit = self.cleaned_data.get("business_unit")
        for items in BUSINESS_UNITS:
            if business_unit in items:
                new_business_unit = items[1]
        return new_business_unit

    def clean_role(self, *args, **kwargs):
        role = self.cleaned_data.get("role")
        for items in ROLES:
            if role in items:
                new_role = items[1]
        return new_role

    def clean_site(self, *args, **kwargs):
        site = self.cleaned_data.get("site")
        for items in SITE_NAMES:
            if site in items:
                new_site = items[1]
        return new_site


# class MvpUserRequestForm(forms.ModelForm):
#     # Start_Date = forms.DateTimeField()
#     # End_Date = forms.DateTimeField()
#     # End_Time = forms.DateTimeField()
#     # Start_Time = forms.DateTimeField()
#     class Meta:
#         model = MvpUserRequest
#         fields = [
#             'user_ID',
#             'Name',
#             'Start_Date',
#             'Start_Time',
#             'End_Date',
#             'End_Time',
#             'Activity',
#             'Mul_Over',
#             'BreakTime'
#         ]
#         widgets = {
#             'user_ID': forms.TextInput(
#                 attrs={'placeholder': 'Please give the ID of  the requesting person'}),
#             'Name': forms.TextInput(
#                 attrs={'placeholder': 'Please give the Name of  the requesting person'}),
#             'Start_Date': forms.SelectDateWidget(years=YEAR_CHOICES),
#             'Start_Time': forms.TextInput(
#                 attrs={'placeholder': '##:##'}),
#             'End_Date': forms.SelectDateWidget(years=YEAR_CHOICES),
#             'End_Time': forms.TextInput(
#                 attrs={'placeholder': '##:##'}),
#             'Activity': forms.TextInput(
#                 attrs={'placeholder': 'Select an activity'}),
#             'Mul_Over': forms.TextInput(
#                 attrs={'placeholder': 'Multiplicator Or Overlap time?'}),
#             # 'Timezone': forms.TextInput(disabled=True),
#             'BreakTime': forms.TextInput(
#                 attrs={'placeholder': 'Please give the Break Time email address of the requesting person'})
#             # 'Status': forms.TextInput(disabled=True)
#
#         }


class OverTimeUserRequestForm(forms.ModelForm):
    # Start_Date = forms.DateTimeField()
    # End_Date = forms.DateTimeField()
    # # End_Time = forms.DateTimeField()
    # Start_Time = forms.CharField(label='Start_Time', required=True, widget=forms.TextInput(
    #     attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}))
    #
    # End_Time = forms.CharField(label='End_Time', required=True, widget=forms.TextInput(
    #     attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}))

    Activity = forms.ChoiceField(label='Activity', required=True, choices=OT_ACTIVITY,
                                 widget=forms.Select(attrs={'class': 'select'}))

    Mul_Over = forms.ChoiceField(label='Multiplicator', required=True, choices=OT_MULTIPLICATOR,
                                 widget=forms.Select(attrs={'class': 'select'}))

    Name = forms.ChoiceField(label='Type of OT', required=True, choices=OT_TYPES,
                             widget=forms.Select(attrs={'class': 'select'}))
    BreakTime = forms.ChoiceField(label='Choose Break Time', required=True, choices=BREAK,
                                  widget=forms.Select(attrs={'class': 'select'}))

    class Meta:
        model = MvpUserRequest
        fields = [
            'user_ID',
            'Name',
            'Start_Date',
            'Start_Time',
            'End_Date',
            'End_Time',
            'Activity',
            'Mul_Over',
            'BreakTime'
        ]
        widgets = {
            'user_ID': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text',
                       'placeholder': 'Please give the ID of  the requesting person'}),
            # 'Name': forms.RadioSelect,
            'Start_Date': forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class':
                                                                                'select'}),
            'Start_Time': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}),
            'End_Date': forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class':
                                                                              'select'}),
            'End_Time': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}),
            # 'BreakTime': forms.TextInput(
            # attrs={'class': 'input is-primary', 'type': 'text',
            #        'placeholder': 'Please give the Break Time'}),
            # 'Activity': forms.Select(attrs={'class': 'select'})
            # 'Status': forms.TextInput(disabled=True)

        }
        labels = {
            'user_ID': 'Employee ID',
            # 'Name': 'Type of OT',
            'Start_Time': 'Start Time',
            'End_Time': 'End Time'
        }

    def clean_user_number(self, *args, **kwargs):
        u_id = self.cleaned_data.get("user_ID")
        if len(u_id) != 7:
            raise ValidationError("Please enter valid employee ID")
        else:

            final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(u_id)  # 3054204"
            final_headers = {
                "x-api-key": "lsUfB4oaUX"
            }
            try:
                # fin = requests.get(final_url, final_headers, False)
                # print(username[5:])
                fin = requests.get(final_url, headers=final_headers, verify=False)

                # temp_data_json = json.loads(json.dumps(fin.json()))

                temp_data_json = json.loads(json.dumps(fin.json()))
                return str(temp_data_json['id'])
            except ConnectionError and KeyError:
                return "Please enter a valid employee number"

    def for_Name(self, *args, **kwargs):
        u_id = self.cleaned_data.get("user_ID")
        if len(u_id) != 7:
            raise ValidationError("Please enter valid employee ID")
        else:

            final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(u_id)  # 3054204"
            final_headers = {
                "x-api-key": "lsUfB4oaUX"
            }
            try:
                # fin = requests.get(final_url, final_headers, False)
                # print(username[5:])
                fin = requests.get(final_url, headers=final_headers, verify=False)

                # temp_data_json = json.loads(json.dumps(fin.json()))

                temp_data_json = json.loads(json.dumps(fin.json()))
                return str(temp_data_json['firstName'])
            except ConnectionError and KeyError:
                return "Please enter a valid employee number"

    def clean(self):
        cleaned_data = super(OverTimeUserRequestForm, self).clean()
        user_id = cleaned_data.get("user_ID")
        name = cleaned_data.get("Name")
        str_time = cleaned_data.get('Start_Time')
        end_time = cleaned_data.get('End_Time')
        str_date = cleaned_data.get('Start_Date')
        end_date = cleaned_data.get('End_Date')
        breaktime = cleaned_data.get('BreakTime')

        if user_id and str_time and end_time:
            # Only do something if both fields are valid so far.
            # print(type(str_date))
            str_date = datetime.strptime(str_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            past = datetime.now() - timedelta(days=7)
            if len(user_id) != 7:
                # self.add_error('user_ID', forms.ValidationError("neekenduku"))
                raise forms.ValidationError({'user_ID': 'Please enter a valid ID (7 numbers)'})
            else:
                if str_date < past or end_date < past:
                    self.errors['Start_Date'] = ["Please select a date no later tham 7 days from current day"]
                    self.errors['End_Date'] = ["Please select a date no later tham 7 days from current day"]
                    # raise ValidationError("Please enter start/end date no later than 7 days from now")
                else:
                    if str_date > end_date:
                        self.errors['Start Date'] = [u'Enter valid start ID, it should be less than start date']
                        # raise ValidationError("Please enter start date less than end date")
                    else:
                        if len(str_time) != 5 and ":" not in str_time:
                            self.errors['Start_Time'] = [u'Enter valid start time']
                        else:
                            str_time_split = str_time.split(":")
                            str_hour = str_time_split[0]
                            str_min = str_time_split[1]
                            try:
                                str_hour = int(str_hour)
                                str_min = int(str_min)

                                print(str(str_hour))
                                print(str(str_min))
                                if str_hour > 23 or str_hour < 0 or str_min > 59 or str_min < 0:
                                    self.errors['Start_Time'] = [u'Enter valid start time']
                                else:
                                    if len(end_time) != 5 and ":" not in end_time:
                                        self.errors['End_Time'] = [u'Enter valid end time']
                                    else:
                                        end_time_split = end_time.split(":")
                                        end_hour = end_time_split[0]
                                        end_min = end_time_split[1]
                                        try:
                                            end_hour = int(end_hour)
                                            end_min = int(end_min)
                                            if end_hour > 23 or end_hour < 0 or end_min > 59 or end_min < 0:
                                                self.errors['End_Time'] = [u'Enter valid end time']
                                            else:
                                                try:
                                                    start_time_date = datetime.strptime(str_time, '%H:%M')
                                                    end_time_date = datetime.strptime(end_time, '%H:%M')
                                                    if start_time_date > end_time_date:
                                                        self.errors['Start_Time'] = [
                                                            u'Please enter valid start time & end time, Start time should be less than end time']
                                                        self.errors['End_Time'] = [
                                                            u'Please enter valid start time & end time, Start time should be less than end time']
                                                except ValueError:
                                                    self.errors['Start_Time'] = [
                                                        u'Please enter valid start time & end time, Start time should be less than end time']
                                                    self.errors['End_Time'] = [
                                                        u'Please enter valid start time & end time, Start time should be less than end time']

                                                    ##############################
                                                u_id = self.cleaned_data.get("user_ID")
                                                if len(u_id) != 7:
                                                    self.errors['user_ID'] = [
                                                        u'Please enter valid user ID']
                                                else:

                                                    final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(
                                                        u_id)  # 3054204"
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

                                                        if country == 'IND':
                                                            if "full" in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) < 9:
                                                                raise ValidationError({
                                                                    'Start_Time': 'Please enter valid start/end time : For a full day OT please choose 9 hrs'})
                                                            elif "full" not in name and (
                                                                    (end_time_date - start_time_date)).seconds < 3600:
                                                                raise ValidationError({'Start_Time':
                                                                                           'Please enter valid start/end time : Given OT to plot is ' + str(
                                                                                               (((
                                                                                                       end_time_date - start_time_date)).seconds) / 60) + ' mins, minimum is one hour'})
                                                            if "full" in name and "lunch_45" != breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           'Please select appropriate '
                                                                                           'break time : full day should '
                                                                                           'have lunch and 45 mins break'})
                                                            if "full" not in name and ((((
                                                                    end_time_date - start_time_date)).seconds / 60) / 60) == 8 and "lunch_30" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           'Please select appropriate break time : 8 hrs a day should have lunch and 30 mins break'})
                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 7 and "lunch_15" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           'Please select appropriate break time : 7 hrs a day should have lunch and 15 mins break'})
                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 5 and "lunch_15" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           "Please select appropriate break time : 5 hrs a day should have lunch and 15 mins break"})
                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 6 and "lunch_15" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           "Please select appropriate break time : 6 hrs a day should have lunch and 15 mins break"})

                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 4 and "15min" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           '4 hrs a day should have 15 mins break'})
                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 2 and "15min" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           '2 hrs a day should have 15 mins break'})
                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 3 and "15min" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           '3 hrs a day should have 15 mins break'})
                                                            if "full" not in name and (
                                                                    (((
                                                                            end_time_date - start_time_date)).seconds / 60) / 60) == 1 and "no" not in breaktime:
                                                                raise ValidationError({'BreakTime':
                                                                                           '1 hrs a day should not have break time'})


                                                    except ConnectionError and KeyError:
                                                        self.errors['user_ID'] = [
                                                            u'Please enter valid user ID']

                                        except ValueError:
                                            self.errors['End_Time'] = [u'Enter valid end time']


                            except ValueError:
                                self.errors['Start_Time'] = [u'Enter valid start time']

                                #####################################



        else:
            self.errors['user_ID'] = [
                u'Please enter valid user ID']
            # raise ValidationError(
            #     "Not a valid input, Please try again with correct input"
            # )
        return cleaned_data

    def clean_activity(self, *args, **kwargs):
        activity = self.cleaned_data.get("Activity")
        for items in OT_ACTIVITY:
            if activity in items:
                new_activity = items[1]
        return new_activity

    def clean_mul_over(self, *args, **kwargs):
        mul = self.cleaned_data.get("Mul_Over")
        for items in OT_MULTIPLICATOR:
            if mul in items:
                new_mul = items[1]
        return new_mul


class TeleOptiUserRequestForm(forms.ModelForm):
    # Start_Date = forms.DateTimeField()
    # End_Date = forms.DateTimeField()
    # End_Time = forms.DateTimeField()
    # Start_Time = forms.DateTimeField()
    Start_Time = forms.CharField(label='Start_Time', required=True, widget=forms.TextInput(
        attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}))

    End_Time = forms.CharField(label='End_Time', required=True, widget=forms.TextInput(
        attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}))

    Activity = forms.ChoiceField(label='Activity', required=True, choices=TELEOPTI_ACTIVITY,
                                 widget=forms.Select(attrs={'class': 'select'}))

    Mul_Over = forms.ChoiceField(label='OverLap Status', required=True, choices=TELEOPTI_OVERLAP,
                                 widget=forms.Select(attrs={'class': 'select'}))

    class Meta:
        model = MvpUserRequest
        fields = [
            'user_ID',
            'Start_Date',
            'Start_Time',
            'End_Date',
            'End_Time',
            'Activity',
            'Mul_Over'
        ]
        widgets = {
            'user_ID': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text',
                       'placeholder': 'Please give the ID of  the requesting person'}),
            'Name': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text',
                       'placeholder': 'Please give the Name of  the requesting person'}),
            'Start_Date': forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class':
                                                                                'select'}),
            'Start_Time': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}),
            'End_Date': forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class':
                                                                              'select'}),
            'End_Time': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text', 'placeholder': '##:##'}),
            'BreakTime': forms.TextInput(
                attrs={'class': 'input is-primary', 'type': 'text',
                       'placeholder': 'Please give the Break Time'}),
            # 'Activity': forms.Select(attrs={'class': 'select'})
            # 'Status': forms.TextInput(disabled=True)

        }
        labels = {
            'user_ID': 'Employee ID',
            'Name': 'Employee Name',
            'Start_Time': 'Start Time',
            'End_Time': 'End Time'
        }

    def clean_user_number(self, *args, **kwargs):
        u_id = self.cleaned_data.get("user_ID")
        if len(u_id) != 7:
            raise ValidationError("Please enter valid employee ID")
        else:

            final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(u_id)  # 3054204"
            final_headers = {
                "x-api-key": "lsUfB4oaUX"
            }
            try:
                # fin = requests.get(final_url, final_headers, False)
                # print(username[5:])
                fin = requests.get(final_url, headers=final_headers, verify=False)

                # temp_data_json = json.loads(json.dumps(fin.json()))

                temp_data_json = json.loads(json.dumps(fin.json()))
                return str(temp_data_json['id'])
            except ConnectionError and KeyError:
                return "Please enter a valid employee number"

    def for_Name(self, *args, **kwargs):
        u_id = self.cleaned_data.get("user_ID")
        if len(u_id) != 7:
            raise ValidationError("Please enter valid employee ID")
        else:

            final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(u_id)  # 3054204"
            final_headers = {
                "x-api-key": "lsUfB4oaUX"
            }
            try:
                # fin = requests.get(final_url, final_headers, False)
                # print(username[5:])
                fin = requests.get(final_url, headers=final_headers, verify=False)

                # temp_data_json = json.loads(json.dumps(fin.json()))

                temp_data_json = json.loads(json.dumps(fin.json()))
                return str(temp_data_json['firstName'])
            except ConnectionError and KeyError:
                return "Please enter a valid employee number"

    def clean(self):
        cleaned_data = super(TeleOptiUserRequestForm, self).clean()
        user_id = cleaned_data.get("user_ID")
        # name = cleaned_data.get("Name")
        str_time = cleaned_data.get('Start_Time')
        end_time = cleaned_data.get('End_Time')
        str_date = cleaned_data.get('Start_Date')
        end_date = cleaned_data.get('End_Date')
        # breaktime = cleaned_data.get('BreakTime')

        if user_id and str_time and end_time:
            # Only do something if both fields are valid so far.
            # print(type(str_date))
            str_date = datetime.strptime(str_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            past = datetime.now() - timedelta(days=7)
            if len(user_id) != 7:
                # self.add_error('user_ID', forms.ValidationError("neekenduku"))
                raise forms.ValidationError({'user_ID': 'Please enter a valid ID (7 numbers)'})
            else:
                if str_date < past or end_date < past:
                    self.errors['Start_Date'] = ["Please select a date no later tham 7 days from current day"]
                    self.errors['End_Date'] = ["Please select a date no later tham 7 days from current day"]
                    # raise ValidationError("Please enter start/end date no later than 7 days from now")
                else:
                    if str_date > end_date:
                        self.errors['Start Date'] = [u'Enter valid start ID, it should be less than start date']
                        # raise ValidationError("Please enter start date less than end date")
                    else:
                        if len(str_time) != 5 and ":" not in str_time:
                            self.errors['Start_Time'] = [u'Enter valid start time']
                        else:
                            str_time_split = str_time.split(":")
                            str_hour = str_time_split[0]
                            str_min = str_time_split[1]
                            try:
                                str_hour = int(str_hour)
                                str_min = int(str_min)

                                print(str(str_hour))
                                print(str(str_min))
                                if str_hour > 23 or str_hour < 0 or str_min > 59 or str_min < 0:
                                    self.errors['Start_Time'] = [u'Enter valid start time']
                                else:
                                    if len(end_time) != 5 and ":" not in end_time:
                                        self.errors['End_Time'] = [u'Enter valid end time']
                                    else:
                                        end_time_split = end_time.split(":")
                                        end_hour = end_time_split[0]
                                        end_min = end_time_split[1]
                                        try:
                                            end_hour = int(end_hour)
                                            end_min = int(end_min)
                                            if end_hour > 23 or end_hour < 0 or end_min > 59 or end_min < 0:
                                                self.errors['End_Time'] = [u'Enter valid end time']
                                            else:
                                                try:
                                                    start_time_date = datetime.strptime(str_time, '%H:%M')
                                                    end_time_date = datetime.strptime(end_time, '%H:%M')
                                                    if start_time_date > end_time_date:
                                                        self.errors['Start_Time'] = [
                                                            u'Please enter valid start time & end time, Start time should be less than end time']
                                                        self.errors['End_Time'] = [
                                                            u'Please enter valid start time & end time, Start time should be less than end time']
                                                except ValueError:
                                                    self.errors['Start_Time'] = [
                                                        u'Please enter valid start time & end time, Start time should be less than end time']
                                                    self.errors['End_Time'] = [
                                                        u'Please enter valid start time & end time, Start time should be less than end time']

                                                    ##############################
                                                u_id = self.cleaned_data.get("user_ID")
                                                if len(u_id) != 7:
                                                    self.errors['user_ID'] = [
                                                        u'Please enter valid user ID']
                                                else:

                                                    final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(
                                                        u_id)  # 3054204"
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

                                                    except ConnectionError and KeyError:
                                                        self.errors['user_ID'] = [
                                                            u'Please enter valid user ID']

                                        except ValueError:
                                            self.errors['End_Time'] = [u'Enter valid end time']


                            except ValueError:
                                self.errors['Start_Time'] = [u'Enter valid start time']

                                #####################################



        else:
            self.errors['user_ID'] = [
                u'Please enter valid user ID']
            # raise ValidationError(
            #     "Not a valid input, Please try again with correct input"
            # )
        return cleaned_data

    def clean_activity(self, *args, **kwargs):
        activity = self.cleaned_data.get("Activity")
        for items in TELEOPTI_ACTIVITY:
            if activity in items:
                new_activity = items[1]
        return new_activity

    def clean_mul_over(self, *args, **kwargs):
        mul = self.cleaned_data.get("Mul_Over")
        for items in TELEOPTI_OVERLAP:
            if mul in items:
                new_mul = items[1]
        return new_mul
