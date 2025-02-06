from django.db import models
from apps.pim.models import Product
from apps.accounts.models import User
from django.core.validators import FileExtensionValidator

class Warehouse(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Customer(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    customerno = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

class SalesOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('picking', 'Picking'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    documents = models.ManyToManyField('SalesOrderDocument', blank=True,  related_name='sales_orders_documents')
    is_fba_shipment = models.BooleanField(default=False)
    shipping_label = models.FileField(upload_to='shipping_labels/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    local_trackingnr = models.CharField(max_length=100, blank=True, null=True)
    local_tracktrace_url = models.URLField(blank=True, null=True)
    global_trackingnr = models.CharField(max_length=100, blank=True, null=True)
    global_tracktrace_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderProduct(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    asin_sticker = models.CharField(max_length=100, blank=True, null=True)  # Optional ASIN sticker field

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class SalesOrderDocument(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='sales_order')
    document = models.FileField(upload_to='sales_order_documents/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'jpeg', 'png'])])

    def __str__(self):
        return f"Document for Order #{self.order.id}"

class Collie(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='collies')
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shipping_label = models.FileField(upload_to='shipping_labels/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    def __str__(self):
        return f"Collie for Order #{self.sales_order.id}"

class CollieProduct(models.Model):
    collie = models.ForeignKey(Collie, on_delete=models.CASCADE, related_name='products')
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order_product.product.name} - {self.quantity}"