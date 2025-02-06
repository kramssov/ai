from django.db import models
from apps.accounts.models import User

class Consignee(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consignees')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=12, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    house_no = models.CharField(max_length=60, blank=True, null=True)
    addition = models.CharField(max_length=60, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name