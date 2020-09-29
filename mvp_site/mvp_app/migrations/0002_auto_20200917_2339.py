# Generated by Django 2.1.15 on 2020-09-18 06:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mvp_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvp',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2020, 9, 18, 6, 39, 29, 129564, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mvp',
            name='emp_ID',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='mvp',
            name='emp_Name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='mvp',
            name='location',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='mvp',
            name='req_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='mvp',
            name='user_req',
            field=models.CharField(max_length=100),
        ),
    ]
