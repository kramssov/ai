from django.urls import path
from .views import manage_warehouse, create_warehouse, manage_customers, create_customer, update_customer, delete_customer

urlpatterns = [
    path('manage/', manage_warehouse, name='manage_warehouse'),
    path('warehouse/create/', create_warehouse, name='create_warehouse'),
    path('customers/', manage_customers, name='manage_customers'),
    path('customer/create/', create_customer, name='create_customer'),
    path('customer/update/<int:customer_id>/', update_customer, name='update_customer'),
    path('customer/delete/<int:customer_id>/', delete_customer, name='delete_customer'),
]