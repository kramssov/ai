from django.db import models
from apps.accounts.models import User
from apps.pim.models import Product
from apps.warehouse.models import SalesOrder, OrderProduct, SalesOrderDocument

class TenantWarehouse(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class TenantCustomer(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    customerno = models.IntegerField(unique=True)

    def __str__(self):
        return self.name