from django.contrib import admin
# Register your models here.
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_buyer', 'is_supplier']


admin.site.register(User, UserAdmin)