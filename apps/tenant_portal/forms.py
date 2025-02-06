from django import forms
from .models import TenantWarehouse, TenantCustomer

class TenantWarehouseForm(forms.ModelForm):
    class Meta:
        model = TenantWarehouse
        fields = ['name', 'location']

class TenantCustomerForm(forms.ModelForm):
    class Meta:
        model = TenantCustomer
        fields = ['name', 'address', 'email', 'phone', 'customerno']