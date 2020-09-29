from django import forms
import re
from .models import Mvp, MvpUserRequest
from email.utils import parseaddr
import re

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


class MvpForm(forms.ModelForm):
    emp_ID = forms.CharField(label='Employee ID', required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Please give the employee ID of the requesting person'}))
    emp_Name = forms.CharField(label='Employee Name', required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Please give the employee Name of the requesting person'}))

    supervisor = forms.CharField(label='Supervisor Name', required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Please give the Supervisor ID of the requesting person'}))
    email = forms.CharField(label='Email Address', required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Please give the employee email address of the requesting person'}))

    role = forms.ChoiceField(label='Role', required=True, choices=ROLES)
    site = forms.ChoiceField(label='Site', required=True, choices=SITE_NAMES)
    campaign = forms.ChoiceField(label='Campaign', required=True, choices=CAMPAIGNS)
    business_unit = forms.ChoiceField(label='Business Unit', required=True, choices=BUSINESS_UNITS)

    location = forms.ChoiceField(label='Location', required=True, choices=LOCATIONS)
    req_type = forms.ChoiceField(label='Request Type', required=True, choices=REQUEST_TYPES)

    user_req = forms.ChoiceField(
        label='User Request Type',
        choices=USERS_REQ_TYPE,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Mvp
        fields = [
            'emp_ID',
            'emp_Name',
            'location',
            'req_type',
            'supervisor',
            'email',
            'role',
            'site',
            'campaign',
            'business_unit',
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
    # End_Time = forms.DateTimeField()
    Start_Time = forms.CharField(label='Start_Time', required=True, widget=forms.TextInput(
        attrs={'placeholder': '##:##'}))

    End_Time = forms.CharField(label='End_Time', required=True, widget=forms.TextInput(
        attrs={'placeholder': '##:##'}))

    Activity = forms.ChoiceField(label='Activity', required=True, choices=OT_ACTIVITY)

    Mul_Over = forms.ChoiceField(label='Multiplicator', required=True, choices=OT_MULTIPLICATOR)

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
                attrs={'placeholder': 'Please give the ID of  the requesting person'}),
            'Name': forms.TextInput(
                attrs={'placeholder': 'Please give the Name of  the requesting person'}),
            'Start_Date': forms.SelectDateWidget(years=YEAR_CHOICES),
            # 'Start_Time': forms.TextInput(
            #     attrs={'placeholder': '##:##'}),
            'End_Date': forms.SelectDateWidget(years=YEAR_CHOICES),
            # 'End_Time': forms.TextInput(
            #     attrs={'placeholder': '##:##'}),
            'BreakTime': forms.TextInput(
                attrs={'placeholder': 'Please give the Break Time email address of the requesting person'})
            # 'Status': forms.TextInput(disabled=True)

        }

        def clean_activity(self, *args, **kwargs):
            act = self.cleaned_data.get("Activity")
            for items in OT_ACTIVITY:
                if act in items:
                    new_act = items[1]
            return new_act

        def clean_mul(self, *args, **kwargs):
            mul = self.cleaned_data.get("Mul_Over")
            for items in OT_MULTIPLICATOR:
                if mul in items:
                    new_mul = items[1]
            return new_mul

        def clean_Start_Time(self, *args, **kwargs):
            time = self.cleaned_data.get("Start_Time")
            r = re.compile('.*:.*')
            if ":" in time and int(time.split(":")[0]).isdecimal() and int(time.split(":")[1]).isdecimal():
                return time
            else:
                raise forms.ValidationError("This is not a valid time format")

        def clean_End_Time(self, *args, **kwargs):
            time = self.cleaned_data.get("End_Time")
            if ":" in time and int(time.split(":")[0]).isdecimal() and int(time.split(":")[1]).isdecimal():
                return time
            else:
                raise forms.ValidationError("This is not a valid time format")


class TeleOptiUserRequestForm(forms.ModelForm):
    # Start_Date = forms.DateTimeField()
    # End_Date = forms.DateTimeField()
    # End_Time = forms.DateTimeField()
    # Start_Time = forms.DateTimeField()
    Start_Time = forms.CharField(label='Start_Time', required=True, widget=forms.TextInput(
        attrs={'placeholder': '##:##'}))

    End_Time = forms.CharField(label='End_Time', required=True, widget=forms.TextInput(
        attrs={'placeholder': '##:##'}))

    Activity = forms.ChoiceField(label='Activity', required=True, choices=TELEOPTI_ACTIVITY)

    Mul_Over = forms.ChoiceField(label='OverLap Status', required=True, choices=TELEOPTI_OVERLAP)

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
            'Mul_Over'
        ]
        widgets = {
            'user_ID': forms.TextInput(
                attrs={'placeholder': 'Please give the ID of  the requesting person'}),
            'Name': forms.TextInput(
                attrs={'placeholder': 'Please give the Name of  the requesting person'}),
            'Start_Date': forms.SelectDateWidget(years=YEAR_CHOICES),
            # 'Start_Time': forms.TextInput(
            #     attrs={'placeholder': '##:##'}),
            'End_Date': forms.SelectDateWidget(years=YEAR_CHOICES),
            # 'End_Time': forms.TextInput(
            #     attrs={'placeholder': '##:##'}),
            'BreakTime': forms.TextInput(
                attrs={'placeholder': 'Please give the Break Time email address of the requesting person'})
            # 'Status': forms.TextInput(disabled=True)

        }

        def clean_activity(self, *args, **kwargs):
            act = self.cleaned_data.get("Activity")
            for items in TELEOPTI_ACTIVITY:
                if act in items:
                    new_act = items[1]
            return new_act

        def clean_mul(self, *args, **kwargs):
            mul = self.cleaned_data.get("Mul_Over")
            for items in TELEOPTI_OVERLAP:
                if mul in items:
                    new_mul = items[1]
            return new_mul

        def clean_Start_Time(self, *args, **kwargs):
            time = self.cleaned_data.get("Start_Time")
            r = re.compile('.*:.*')
            if ":" in time:
                return time
            else:
                raise forms.ValidationError("This is not a valid time format")

        def clean_End_Time(self, *args, **kwargs):
            time = self.cleaned_data.get("End_Time")
            r = re.compile('.*:.*')
            if ":" in time:
                return time
            else:
                raise forms.ValidationError("This is not a valid time format")