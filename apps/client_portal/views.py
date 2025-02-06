from django.shortcuts import render, redirect, get_object_or_404
from .models import ClientCustomer
from .forms import ClientCustomerForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.pim.models import Product
from apps.warehouse.models import SalesOrder, OrderProduct, SalesOrderDocument

@login_required
def create_sales_order(request):
    if request.user.role not in ['client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to create sales orders.")
    if request.method == 'POST':
        order_form = SalesOrderForm(request.POST, request.FILES)
        order_products_data = request.POST.getlist('order_products[]')
        document_form = SalesOrderDocumentForm(request.POST, request.FILES)
        if order_form.is_valid() and document_form.is_valid():
            sales_order = order_form.save(commit=False)
            sales_order.tenant = request.user.tenant
            sales_order.save()
            for product_id, quantity, asin_sticker in zip(order_products_data[::3], order_products_data[1::3], order_products_data[2::3]):
                product = get_object_or_404(Product, id=product_id, tenant=request.user.tenant, status='approved')
                OrderProduct.objects.create(order=sales_order, product=product, quantity=int(quantity), asin_sticker=asin_sticker)
            document = document_form.save(commit=False)
            document.order = sales_order
            document.save()
            return redirect('view_orders')
    else:
        order_form = SalesOrderForm()
        products = Product.objects.filter(tenant=request.user.tenant, status='approved')
        document_form = SalesOrderDocumentForm()
    return render(request, 'client_portal/create_sales_order.html', {'order_form': order_form, 'products': products, 'document_form': document_form})

@login_required
def view_orders(request):
    if request.user.role not in ['client_admin', 'client_logistics_manager', 'client_fba_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to view sales orders.")
    orders = SalesOrder.objects.filter(tenant=request.user.tenant)
    return render(request, 'client_portal/view_orders.html', {'orders': orders})

@login_required
def track_sales_order(request, order_id):
    if request.user.role not in ['client_admin', 'client_logistics_manager', 'client_fba_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to track sales orders.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    return render(request, 'client_portal/track_sales_order.html', {'sales_order': sales_order})