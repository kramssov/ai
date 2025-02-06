from django.shortcuts import render, redirect
from .forms import TenantForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.accounts.models import User

@login_required
def create_tenant(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You do not have permission to create tenants.")
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'tenant_admin'
            user.set_password(user.password)
            user.save()
            messages.success(request, "Tenant created successfully.")
            return redirect('create_tenant')
    else:
        form = TenantForm()
    return render(request, 'admin_portal/create_tenant.html', {'form': form})