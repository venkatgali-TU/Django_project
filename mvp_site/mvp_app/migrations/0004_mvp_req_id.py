# Generated by Django 2.1 on 2020-09-19 08:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mvp_app', '0003_auto_20200918_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvp',
            name='req_ID',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
