from django.shortcuts import render, redirect, get_object_or_404
from .models import Consignee
from .forms import ConsigneeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def consignee_list(request):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to view consignees.")
    consignees = Consignee.objects.filter(tenant=request.user.tenant)
    return render(request, 'crm/consignee_list.html', {'consignees': consignees})

@login_required
def consignee_create(request):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to create consignees.")
    if request.method == 'POST':
        form = ConsigneeForm(request.POST)
        if form.is_valid():
            consignee = form.save(commit=False)
            consignee.tenant = request.user.tenant
            consignee.save()
            messages.success(request, "Consignee created successfully.")
            return redirect('consignee_list')
    else:
        form = ConsigneeForm()
    return render(request, 'crm/consignee_create.html', {'form': form})

@login_required
def consignee_update(request, consignee_id):
    consignee = get_object_or_404(Consignee, id=consignee_id, tenant=request.user.tenant)
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to update consignees.")
    if request.method == 'POST':
        form = ConsigneeForm(request.POST, instance=consignee)
        if form.is_valid():
            form.save()
            messages.success(request, "Consignee updated successfully.")
            return redirect('consignee_list')
    else:
        form = ConsigneeForm(instance=consignee)
    return render(request, 'crm/consignee_update.html', {'form': form, 'consignee': consignee})

@login_required
def consignee_delete(request, consignee_id):
    consignee = get_object_or_404(Consignee, id=consignee_id, tenant=request.user.tenant)
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to delete consignees.")
    if request.method == 'POST':
        consignee.delete()
        messages.success(request, "Consignee deleted successfully.")
        return redirect('consignee_list')
    return render(request, 'crm/consignee_delete.html', {'consignee': consignee})