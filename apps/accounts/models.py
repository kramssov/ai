from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('tenant_admin', 'Tenant Admin'),
        ('warehouse_manager', 'Warehouse Manager'),
        ('client', 'Client'),
        ('client_admin', 'Client Admin'),
        ('client_logistics_manager', 'Client Logistics Manager'),
        ('client_fba_manager', 'Client FBA Manager'),
        ('client_logistics_worker', 'Client Logistics Worker'),
        ('client_fba_worker', 'Client FBA Worker'),
    )

    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default='client')
    tenant = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='clients')
    easytrans_username = models.CharField(max_length=100, blank=True, null=True)
    easytrans_password = models.CharField(max_length=100, blank=True, null=True)
    easytrans_server = models.CharField(max_length=100, blank=True, null=True)
    easytrans_environment = models.CharField(max_length=100, blank=True, null=True)
    sendcloud_api_key = models.CharField(max_length=100, blank=True, null=True)
    sendcloud_api_secret = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )