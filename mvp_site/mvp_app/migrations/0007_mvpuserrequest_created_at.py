# Generated by Django 2.1 on 2020-10-08 07:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mvp_app', '0006_mvpuserrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvpuserrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
