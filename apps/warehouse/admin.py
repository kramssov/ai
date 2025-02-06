from django.contrib import admin
from .models import SalesOrder, OrderProduct, Product, Customer, SalesOrderDocument, Collie, CollieProduct

admin.site.register(SalesOrder)
admin.site.register(OrderProduct)
admin.site.register(Customer)
admin.site.register(SalesOrderDocument)
admin.site.register(Collie)
admin.site.register(CollieProduct)