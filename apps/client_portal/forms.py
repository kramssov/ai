from django import forms
from .models import ClientCustomer

class ClientCustomerForm(forms.ModelForm):
    class Meta:
        model = ClientCustomer
        fields = ['name', 'address', 'email', 'phone', 'customerno']