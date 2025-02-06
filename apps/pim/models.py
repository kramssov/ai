from django.db import models
from apps.accounts.models import User
from django.core.validators import FileExtensionValidator

class Product(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    )

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    whsku = models.CharField(max_length=10, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    asin = models.CharField(max_length=100, blank=True, null=True)  # Optional ASIN field
    images = models.ManyToManyField('ProductImage', blank=True,  related_name='products_images')

    def save(self, *args, **kwargs):
        if not self.whsku:
            self.whsku = self.generate_unique_whsku()
        super().save(*args, **kwargs)

    def generate_unique_whsku(self):
        # Get the last WHSKU for the tenant and increment it
        last_product = Product.objects.filter(tenant=self.tenant).order_by('-whsku').first()
        if last_product:
            last_whsku = int(last_product.whsku, 36) + 1
        else:
            last_whsku = 1
        return f"{last_whsku:010x}"  # Format as 10-character alphanumeric string

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images_test')
    image = models.ImageField(upload_to='product_images/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return f"Image for {self.product.name}"