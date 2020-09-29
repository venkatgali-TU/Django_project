from django.contrib import admin

# Register your models here.
from .models import Mvp


class Mvp_Admin(admin.ModelAdmin):
    pass


admin.site.register(Mvp,Mvp_Admin)