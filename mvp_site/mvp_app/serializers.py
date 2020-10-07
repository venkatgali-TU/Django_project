from rest_framework import serializers
from .models import MvpUserRequest, Mvp


class MvpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MvpUserRequest
        fields = ('user_ID',
                  'Name',
                  'Start_Date',
                  'Start_Time',
                  'End_Date',
                  'End_Time',
                  'Activity',
                  'Mul_Over',
                  'Timezone',
                  'BreakTime',
                  'Status')
