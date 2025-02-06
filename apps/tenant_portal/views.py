from django.shortcuts import render, redirect, get_object_or_404
from .models import TenantWarehouse, TenantCustomer
from .forms import TenantWarehouseForm, TenantCustomerForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.pim.models import Product
from apps.warehouse.models import SalesOrder, OrderProduct, SalesOrderDocument
from apps.warehouse.forms import SalesOrderForm, OrderProductForm, SalesOrderDocumentForm

@login_required
def manage_warehouse(request):
    if request.user.role != 'tenant_admin':
        return HttpResponseForbidden("You do not have permission to manage warehouses.")
    warehouses = TenantWarehouse.objects.filter(tenant=request.user)
    return render(request, 'tenant_portal/manage_warehouse.html', {'warehouses': warehouses})

@login_required
def create_warehouse(request):
    if request.user.role != 'tenant_admin':
        return HttpResponseForbidden("You do not have permission to create warehouses.")
    if request.method == 'POST':
        form = TenantWarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.tenant = request.user
            warehouse.save()
            messages.success(request, "Warehouse created successfully.")
            return redirect('manage_warehouse')
    else:
        form = TenantWarehouseForm()
    return render(request, 'tenant_portal/create_warehouse.html', {'form': form})

@login_required
def manage_customers(request):
    if request.user.role != 'tenant_admin':
        return HttpResponseForbidden("You do not have permission to manage customers.")
    customers = TenantCustomer.objects.filter(tenant=request.user)
    return render(request, 'tenant_portal/manage_customers.html', {'customers': customers})

@login_required
def create_customer(request):
    if request.user.role != 'tenant_admin':
        return HttpResponseForbidden("You do not have permission to create customers.")
    if request.method == 'POST':
        form = TenantCustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tenant = request.user
            customer.save()
            messages.success(request, "Customer created successfully.")
            return redirect('manage_customers')
    else:
        form = TenantCustomerForm()
    return render(request, 'tenant_portal/create_customer.html', {'form': form})

@login_required
def update_customer(request, customer_id):
    if request.user.role != 'tenant_admin':
        return HttpResponseForbidden("You do not have permission to update customers.")
    customer = get_object_or_404(TenantCustomer, id=customer_id, tenant=request.user)
    if request.method == 'POST':
        form = TenantCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect('manage_customers')
    else:
        form = TenantCustomerForm(instance=customer)
    return render(request, 'tenant_portal/update_customer.html', {'form': form})

@login_required
def delete_customer(request, customer_id):
    if request.user.role != 'tenant_admin':
        return HttpResponseForbidden("You do not have permission to delete customers.")
    customer = get_object_or_404(TenantCustomer, id=customer_id, tenant=request.user)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect('manage_customers')
    return render(request, 'tenant_portal/delete_customer.html', {'customer': customer})