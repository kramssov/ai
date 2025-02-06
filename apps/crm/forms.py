from django import forms
from .models import Consignee

class ConsigneeForm(forms.ModelForm):
    class Meta:
        model = Consignee
        fields = ['name', 'address', 'email', 'phone', 'company_name', 'contact_person', 'postal_code', 'city', 'country', 'house_no', 'addition', 'address2']