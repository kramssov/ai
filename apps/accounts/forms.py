from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    tenant = forms.ModelChoiceField(queryset=User.objects.filter(role='tenant_admin'), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'tenant', 'password1', 'password2')

class TenantSignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('tenant_admin', 'Tenant Admin')], required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')