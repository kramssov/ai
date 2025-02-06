from django.urls import path
from .views import product_list, product_create, product_update, product_confirm, product_delete

urlpatterns = [
    path('products/', product_list, name='product_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/update/<int:product_id>/', product_update, name='product_update'),
    path('products/confirm/<int:product_id>/', product_confirm, name='product_confirm'),
    path('products/delete/<int:product_id>/', product_delete, name='product_delete'),
]