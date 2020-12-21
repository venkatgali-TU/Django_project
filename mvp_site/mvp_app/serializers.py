import csv

from rest_framework import serializers

from .models import MvpUserRequest

import json
import requests
import simplejson as json

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MvpSerializer(serializers.HyperlinkedModelSerializer):
    campaign = serializers.SerializerMethodField('campaign_name')
    business_unit = serializers.SerializerMethodField('business_name')
    req_id = serializers.SerializerMethodField('requestid')

    def campaign_name(self, obj):
        field_name = 'user_ID'
        # obj = MvpUserRequest.objects.all().latest('id')
        field_value = getattr(obj, field_name)

        try:
            campaigns = {}
            with open(r'C:\Users\vg3054204\Desktop\roster_campaign.csv', 'rt') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > 1:
                        campaigns[row[0]] = row[1]
            MvpUserRequest.objects.filter(user_ID=str(field_value)).update(
                Timezone=campaigns[obj.user_ID])
            return campaigns[obj.user_ID]
        except:
            MvpUserRequest.objects.filter(user_ID=str(field_value)).update(
                Timezone='')
            return ''
        # field_name = 'user_ID'
        # # obj = MvpUserRequest.objects.all().latest('id')
        # field_value = getattr(obj, field_name)
        #
        # final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(field_value)  # 3054204"
        # final_headers = {
        #     "x-api-key": "lsUfB4oaUX"
        # }
        # try:
        #     # fin = requests.get(final_url, final_headers, False)
        #     # print(username[5:])
        #     fin = requests.get(final_url, headers=final_headers, verify=False)
        #     temp_data_json = json.loads(json.dumps(fin.json()))
        #     MvpUserRequest.objects.filter(user_ID=str(field_value)).update(
        #         Timezone=str(temp_data_json['campaign']['name']))
        #     return str(temp_data_json['campaign']['name'])
        # except ConnectionError and KeyError:
        #     return "Couldnt find the correct campaign name"

    def business_name(self, obj):
        field_name = 'user_ID'
        # obj = MvpUserRequest.objects.first()
        field_value = getattr(obj, field_name)
        final_url = "https://epmsapi.taskus.prv/v1/api/employees/employeeno/" + str(field_value)  # 3054204"
        final_headers = {
            "x-api-key": "lsUfB4oaUX"
        }
        try:
            # fin = requests.get(final_url, final_headers, False)
            # print(username[5:])
            fin = requests.get(final_url, headers=final_headers, verify=False)

            # temp_data_json = json.loads(json.dumps(fin.json()))

            temp_data_json = json.loads(json.dumps(fin.json()))
            result_bus = ""
            if "San Antonio" in str(temp_data_json['site']['location']):
                result_bus = "San Antonio"
            elif "Tijuana" in str(temp_data_json['site']['location']):
                result_bus = "Tijuana"
            elif "New Braunfels" in str(temp_data_json['site']['location']):
                result_bus = "San Antonio"
            elif "Indore" in str(temp_data_json['site']['location']):
                result_bus = "India"
            elif "Greece" in str(temp_data_json['site']['location']):
                result_bus = "Greece"
            elif "Ireland" in str(temp_data_json['site']['location']):
                result_bus = "Ireland"
            elif "La Union" in str(temp_data_json['site']['location']):
                result_bus = "Manila"
            elif "PH" in str(temp_data_json['site']['countryCode']):
                result_bus = "Manila"
            return result_bus
        except ConnectionError and KeyError:
            return "Couldnt find the correct business name"

    def req_id(self, obj):
        field_name = 'Status'
        field_value = getattr(obj, field_name)
        return str(field_value)

    class Meta:
        model = MvpUserRequest
        fields = ('id',
                  'req_id',
                  'user_ID',
                  'Name',
                  'Start_Date',
                  'Start_Time',
                  'End_Date',
                  'End_Time',
                  'Activity',
                  'Mul_Over',
                  'BreakTime',
                  'Status',
                  'campaign',
                  'business_unit',
                  'created_at',
                  'Timezone')
