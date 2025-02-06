from django.urls import path
from .views import create_sales_order, view_orders, track_sales_order

urlpatterns = [
    path('orders/create/', create_sales_order, name='create_sales_order'),
    path('orders/', view_orders, name='view_orders'),
    path('orders/track/<int:order_id>/', track_sales_order, name='track_sales_order'),
]