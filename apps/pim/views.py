from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def product_list(request):
    if request.user.role == 'tenant_admin':
        products = Product.objects.filter(tenant=request.user)
    elif request.user.role in ['client_admin', 'client_logistics_manager', 'client_fba_manager']:
        products = Product.objects.filter(tenant=request.user.tenant)
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")
    return render(request, 'pim/product_list.html', {'products': products})

@login_required
def product_create(request):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to create products.")
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_formset = forms.modelformset_factory(ProductImage, form=ProductImageForm, extra=3)
        images_formset = image_formset(request.POST, request.FILES, queryset=ProductImage.objects.none())
        if form.is_valid() and images_formset.is_valid():
            product = form.save(commit=False)
            product.tenant = request.user if request.user.role == 'tenant_admin' else request.user.tenant
            product.status = 'pending' if request.user.role in ['client_admin', 'client_logistics_manager', 'client_fba_manager'] else 'approved'
            product.save()
            for image_form in images_formset.cleaned_data:
                if image_form:
                    image = image_form['image']
                    photo = ProductImage(product=product, image=image)
                    photo.save()
            if request.user.role in ['client_admin', 'client_logistics_manager', 'client_fba_manager']:
                messages.success(request, "Product created and awaiting approval.")
            else:
                messages.success(request, "Product created and approved.")
            return redirect('product_list')
    else:
        form = ProductForm()
        image_formset = forms.modelformset_factory(ProductImage, form=ProductImageForm, extra=3)
        images_formset = image_formset(queryset=ProductImage.objects.none())
    return render(request, 'pim/product_create.html', {'form': form, 'images_formset': images_formset})

@login_required
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.role == 'tenant_admin' or (request.user.role in ['client_admin', 'client_logistics_manager', 'client_fba_manager'] and product.status == 'pending'):
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            image_formset = forms.modelformset_factory(ProductImage, form=ProductImageForm, extra=3)
            images_formset = image_formset(request.POST, request.FILES, queryset=product.images.all())
            if form.is_valid() and images_formset.is_valid():
                form.save()
                for image_form in images_formset.cleaned_data:
                    if image_form:
                        image = image_form['image']
                        if image:
                            photo = ProductImage(product=product, image=image)
                            photo.save()
                messages.success(request, "Product updated successfully.")
                return redirect('product_list')
        else:
            form = ProductForm(instance=product)
            image_formset = forms.modelformset_factory(ProductImage, form=ProductImageForm, extra=3)
            images_formset = image_formset(queryset=product.images.all())
        return render(request, 'pim/product_update.html', {'form': form, 'product': product, 'images_formset': images_formset})
    else:
        messages.error(request, "You do not have permission to update this product.")
        return redirect('product_list')

@login_required
def product_confirm(request, product_id):
    product = get_object_or_404(Product, id=product_id, tenant=request.user, status='pending')
    if request.method == 'POST':
        product.status = 'approved'
        product.save()
        messages.success(request, "Product approved.")
        return redirect('product_list')
    return render(request, 'pim/product_confirm.html', {'product': product})

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.role == 'tenant_admin':
        product.delete()
        messages.success(request, "Product deleted successfully.")
    elif request.user.role in ['client_admin', 'client_logistics_manager', 'client_fba_manager'] and product.status == 'pending':
        product.delete()
        messages.success(request, "Product deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this product.")
    return redirect('product_list')