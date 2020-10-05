from django.db import models
from datetime import datetime
from django.contrib.sites.models import Site


class Mvp(models.Model):
    emp_ID = models.CharField(max_length=100, blank=False, null=False)
    emp_Name = models.CharField(max_length=100, blank=False, null=False)
    location = models.CharField(max_length=100, blank=False, null=False)
    req_type = models.CharField(max_length=100, blank=False, null=False)
    user_req = models.CharField(max_length=100, blank=False, null=False)
    supervisor = models.CharField(max_length=100, blank=False, null=False)
    email = models.CharField(max_length=100, blank=False, null=False)
    role = models.CharField(max_length=100, blank=False, null=False)
    site = models.CharField(max_length=100, blank=False, null=False)
    campaign = models.CharField(max_length=100, blank=False, null=False)
    business_unit = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)


class MvpUserRequest(models.Model):
    user_ID = models.CharField(max_length=100, blank=False, null=False)
    Name = models.CharField(max_length=100, blank=False, null=False)
    Start_Date = models.CharField(max_length=100, blank=False, null=False)
    Start_Time = models.CharField(max_length=100, blank=False, null=False)
    End_Date = models.CharField(max_length=100, blank=False, null=False)
    End_Time = models.CharField(max_length=100, blank=False, null=False)
    Activity = models.CharField(max_length=100, blank=False, null=False)
    Mul_Over = models.CharField(max_length=100, blank=False, null=False)
    Timezone = models.CharField(max_length=100, blank=False, null=False)
    BreakTime = models.CharField(max_length=100, blank=False, null=False)
    Status = models.CharField(max_length=70, blank=False, null=False)
