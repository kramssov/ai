from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'tenant']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'tenant', 'easytrans_username', 'easytrans_password', 'easytrans_server', 'easytrans_environment', 'sendcloud_api_key', 'sendcloud_api_secret')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'tenant', 'easytrans_username', 'easytrans_password', 'easytrans_server', 'easytrans_environment', 'sendcloud_api_key', 'sendcloud_api_secret')}),
    )

admin.site.register(User, CustomUserAdmin)