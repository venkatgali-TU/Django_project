from rest_framework import serializers

from .models import MvpUserRequest

import json
import requests
import simplejson as json


class MvpSerializer(serializers.HyperlinkedModelSerializer):
    campaign = serializers.SerializerMethodField('campaign_name')
    business_unit = serializers.SerializerMethodField('business_name')
    timeZone = serializers.SerializerMethodField('timezone')

    def campaign_name(self, obj):
        field_name = 'user_ID'
        #obj = MvpUserRequest.objects.all().latest('id')
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
            return str(temp_data_json['campaign']['name'])
        except ConnectionError and KeyError:
            return "Couldnt find the correct campaign name"

    def business_name(self, obj):
        field_name = 'user_ID'
        #obj = MvpUserRequest.objects.first()
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
            return result_bus
        except ConnectionError and KeyError:
            return "Couldnt find the correct business name"

    def timezone(self, obj):
        field_name = 'user_ID'
        #obj = MvpUserRequest.objects.first()
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
            return str(temp_data_json['site']['timeZone'])
        except ConnectionError and KeyError:
            return "Couldnt find the correct timezone"

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.Status = validated_data.get('Status', instance.Status)

        instance.save()
        return instance

    class Meta:
        model = MvpUserRequest
        fields = ('id',
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
                  'timeZone')

    def update(self, instance, validated_data):
        print
        'this - here'
        demo = MvpUserRequest.objects.get(pk=instance.id)
        MvpUserRequest.objects.filter(pk=instance.id) \
            .update(**validated_data)
        return demo


