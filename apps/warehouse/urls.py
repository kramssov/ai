from django.urls import path
from .views import (
    manage_warehouse,
    create_sales_order,
    export_sales_order,
    track_sales_order,
    initiate_picking,
    add_collie,
    add_collie_product,
    finalize_collie,
    select_shipping_provider,
    confirm_shipment,
    export_sales_order_to_sendcloud,
)

urlpatterns = [
    path('manage/', manage_warehouse, name='manage_warehouse'),
    path('sales_order/create/', create_sales_order, name='create_sales_order'),
    path('sales_order/export/<int:order_id>/', export_sales_order, name='export_sales_order'),
    path('sales_order/track/<int:order_id>/', track_sales_order, name='track_sales_order'),
    path('sales_order/initiate_picking/<int:order_id>/', initiate_picking, name='initiate_picking'),
    path('sales_order/add_collie/<int:order_id>/', add_collie, name='add_collie'),
    path('sales_order/add_collie_product/<int:order_id>/<int:collie_id>/', add_collie_product, name='add_collie_product'),
    path('sales_order/finalize_collie/<int:order_id>/<int:collie_id>/', finalize_collie, name='finalize_collie'),
    path('sales_order/select_shipping_provider/<int:order_id>/', select_shipping_provider, name='select_shipping_provider'),
    path('sales_order/export_to_sendcloud/<int:order_id>/', export_sales_order_to_sendcloud, name='export_sales_order_to_sendcloud'),
    path('sales_order/confirm_shipment/<int:order_id>/', confirm_shipment, name='confirm_shipment'),
]