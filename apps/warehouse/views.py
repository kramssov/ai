from django.shortcuts import render, redirect, get_object_or_404
from .models import SalesOrder, OrderProduct, Product, Customer, SalesOrderDocument, Collie, CollieProduct
from apps.crm.models import Consignee  # Correct import statement
from .forms import SalesOrderForm, OrderProductForm, SalesOrderDocumentForm, CollieForm, CollieProductForm
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.files.base import ContentFile
import base64
from io import BytesIO
from reportlab.pdfgen import canvas

@login_required
def manage_warehouse(request):
    if request.user.role not in ['tenant_admin', 'warehouse_manager', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to manage warehouses.")
    sales_orders = SalesOrder.objects.filter(tenant=request.user.tenant)
    return render(request, 'warehouse/manage_warehouse.html', {'sales_orders': sales_orders})

@login_required
def create_sales_order(request):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to create sales orders.")
    if request.method == 'POST':
        order_form = SalesOrderForm(request.POST, request.FILES)
        order_products_data = request.POST.getlist('order_products[]')
        document_form = SalesOrderDocumentForm(request.POST, request.FILES)
        consignee_id = request.POST.get('consignee')
        if order_form.is_valid() and document_form.is_valid():
            sales_order = order_form.save(commit=False)
            sales_order.tenant = request.user if request.user.role == 'tenant_admin' else request.user.tenant
            if consignee_id:
                sales_order.customer = get_object_or_404(Consignee, id=consignee_id, tenant=sales_order.tenant)
            else:
                sales_order.customer = Customer.objects.create(
                    tenant=sales_order.tenant,
                    name=request.POST.get('customer_name'),
                    address=request.POST.get('customer_address'),
                    email=request.POST.get('customer_email'),
                    phone=request.POST.get('customer_phone'),
                    customerno=request.POST.get('customer_customerno'),
                    company_name=request.POST.get('customer_company_name'),
                    contact_person=request.POST.get('customer_contact_person'),
                    postal_code=request.POST.get('customer_postal_code'),
                    city=request.POST.get('customer_city'),
                    country=request.POST.get('customer_country'),
                    house_no=request.POST.get('customer_house_no'),
                    addition=request.POST.get('customer_addition'),
                    address2=request.POST.get('customer_address2'),
                )
            sales_order.save()
            for product_id, quantity, asin_sticker in zip(order_products_data[::3], order_products_data[1::3], order_products_data[2::3]):
                product = get_object_or_404(Product, id=product_id, tenant=sales_order.tenant, status='approved')
                OrderProduct.objects.create(order=sales_order, product=product, quantity=int(quantity), asin_sticker=asin_sticker)
            document = document_form.save(commit=False)
            document.order = sales_order
            document.save()
            return redirect('manage_warehouse')
    else:
        order_form = SalesOrderForm()
        products = Product.objects.filter(tenant=request.user.tenant, status='approved')
        document_form = SalesOrderDocumentForm()
        consignees = Consignee.objects.filter(tenant=request.user.tenant)
    return render(request, 'warehouse/create_sales_order.html', {
        'order_form': order_form,
        'products': products,
        'document_form': document_form,
        'consignees': consignees
    })

@login_required
def export_sales_order(request, order_id):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to export sales orders.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    order_data = {
        "date": sales_order.created_at.strftime("%Y-%m-%d"),
        "time": sales_order.created_at.strftime("%H:%M"),
        "status": "submit",
        "productno": 1,  # Example product number
        "customerno": sales_order.customer.customerno,
        "carrierno": 0,
        "vehicleno": 0,
        "fleetno": 0,
        "substatusno": 0,
        "remark": "Order from FuseHub",
        "remark_invoice": "Order from FuseHub",
        "remark_internal": "Order from FuseHub",
        "remark_purchase": "Order from FuseHub",
        "no_confirmation_email": False,
        "email_receiver": sales_order.customer.email,
        "price": 0,
        "price_description": "Other costs",
        "purchase_price": 0,
        "purchase_price_description": "Other costs",
        "carrier_service": "",
        "carrier_options": "",
        "external_id": str(sales_order.id),
        "order_destinations": [
            {
                "destinationno": 1,
                "collect_deliver": 0,
                "company_name": sales_order.customer.company_name,
                "contact": sales_order.customer.contact_person,
                "address": sales_order.customer.address,
                "houseno": sales_order.customer.house_no,
                "addition": sales_order.customer.addition,
                "address2": sales_order.customer.address2,
                "postal_code": sales_order.customer.postal_code,
                "city": sales_order.customer.city,
                "country": sales_order.customer.country,
                "telephone": sales_order.customer.phone,
                "destination_remark": "Call before delivery",
                "customer_reference": sales_order.customer.customer_reference,
                "delivery_date": sales_order.created_at.strftime("%Y-%m-%d"),
                "delivery_time": sales_order.created_at.strftime("%H:%M"),
                "delivery_time_from": sales_order.created_at.strftime("%H:%M"),
            }
        ],
        "order_packages": [
            {
                "collect_destinationno": 0,
                "deliver_destinationno": 0,
                "ratetypeno": 0,
                "amount": 1,  # Example product number
                "weight": sum(op.product.weight * op.quantity for op in sales_order.products.all()),
                "length": 100,
                "width": 50,
                "height": 30,
                "description": "Various items",
            }
        ],
    }

    if sales_order.is_fba_shipment:
        order_data["remark"] += " (FBA Shipment)"

    credentials = {
        "username": request.user.easytrans_username,
        "password": request.user.easytrans_password,
        "type": "order_import",
        "mode": "effect",
        "return_rates": False,
        "return_documents": "label10x15",  # Request shipping label
        "version": 2
    }

    response = export_sales_order_to_easytrans(order_data, credentials)
    if response.get("error"):
        return render(request, 'warehouse/order_export_error.html', {'error': response["error"]})
    else:
        # Store tracking data in the sales order
        if response.get("result") and response["result"].get("order_tracktrace"):
            tracktrace_data = response["result"]["order_tracktrace"].get(str(sales_order.id))
            if tracktrace_data:
                sales_order.local_trackingnr = tracktrace_data.get("local_trackingnr")
                sales_order.local_tracktrace_url = tracktrace_data.get("local_tracktrace_url")
                sales_order.global_trackingnr = tracktrace_data.get("global_trackingnr")
                sales_order.global_tracktrace_url = tracktrace_data.get("global_tracktrace_url")
                sales_order.status = 'shipped'
                sales_order.save()
        return render(request, 'warehouse/order_exported.html', {'order_id': order_id, 'response': response})

def export_sales_order_to_easytrans(order_data, credentials):
    url = f"https://www.{credentials['server']}/{credentials['environment']}/import_json.php"
    headers = {"Content-Type": "application/json"}
    payload = {
        "authentication": {
            "username": credentials["username"],
            "password": credentials["password"],
            "type": credentials["type"],
            "mode": credentials["mode"],
            "return_rates": credentials["return_rates"],
            "return_documents": credentials["return_documents"],  # Request shipping label
            "version": credentials["version"],
        },
        "orders": [order_data],
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@login_required
def export_sales_order_to_sendcloud(request, order_id):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager']:
        return HttpResponseForbidden("You do not have permission to export sales orders to SendCloud.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    order_data = {
        "api_key": request.user.sendcloud_api_key,
        "api_secret": request.user.sendcloud_api_secret,
        "order": {
            "order_number": str(sales_order.id),
            "invoice_number": str(sales_order.id),
            "email": sales_order.customer.email,
            "status": "new",
            "to_address": {
                "company_name": sales_order.customer.company_name,
                "street": sales_order.customer.address,
                "house_number": sales_order.customer.house_no,
                "city": sales_order.customer.city,
                "postal_code": sales_order.customer.postal_code,
                "country": sales_order.customer.country,
                "phone": sales_order.customer.phone,
            },
            "items": [
                {
                    "sku": op.product.sku,
                    "quantity": op.quantity,
                    "name": op.product.name,
                    "weight": op.product.weight,
                    "description": op.product.description,
                } for op in sales_order.products.all()
            ],
            "shipment": {
                "name": sales_order.customer.name,
                "address": sales_order.customer.address,
                "city": sales_order.customer.city,
                "postal_code": sales_order.customer.postal_code,
                "country": sales_order.customer.country,
                "phone": sales_order.customer.phone,
            },
            "parcel": {
                "package_type": "package",
                "weight": sum(op.product.weight * op.quantity for op in sales_order.products.all()),
                "insured_value": 0,
                "length": 100,
                "width": 50,
                "height": 30,
            },
        }
    }

    url = "https://api.sendcloud.sc/api/public/v1/parcels"
    headers = {
        "Authorization": f"Bearer {request.user.sendcloud_api_key}:{request.user.sendcloud_api_secret}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=order_data, headers=headers)
    response_json = response.json()

    if response_json.get("errors"):
        return render(request, 'warehouse/order_export_error.html', {'error': response_json["errors"]})
    else:
        # Store shipping labels with each collie
        for collie in sales_order.collies.all():
            if response_json.get("data"):
                base64_label = response_json["data"].get("label")
                if base64_label:
                    pdf_file = base64.b64decode(base64_label)
                    collie.shipping_label.save(f"collie_{collie.id}_label.pdf", ContentFile(pdf_file), save=True)
        sales_order.status = 'shipped'
        sales_order.save()
        return render(request, 'warehouse/order_exported.html', {'order_id': order_id, 'response': response_json})

@login_required
def track_sales_order(request, order_id):
    if request.user.role not in ['tenant_admin', 'client_admin', 'client_logistics_manager', 'client_fba_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to track sales orders.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    return render(request, 'warehouse/track_sales_order.html', {'sales_order': sales_order})

@login_required
def initiate_picking(request, order_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to initiate picking.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    if sales_order.status != 'pending':
        return HttpResponseForbidden("This sales order cannot be picked at this stage.")
    sales_order.status = 'picking'
    sales_order.save()
    return redirect('manage_warehouse')

@login_required
def add_collie(request, order_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to add collies.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    if sales_order.status != 'picking':
        return HttpResponseForbidden("This sales order cannot be packed at this stage.")
    if request.method == 'POST':
        form = CollieForm(request.POST)
        if form.is_valid():
            collie = form.save(commit=False)
            collie.sales_order = sales_order
            collie.save()
            return redirect('add_collie_product', order_id=order_id, collie_id=collie.id)
    else:
        form = CollieForm()
    return render(request, 'warehouse/add_collie.html', {'form': form, 'sales_order': sales_order})

@login_required
def add_collie_product(request, order_id, collie_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to add products to collies.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    collie = get_object_or_404(Collie, id=collie_id, sales_order=sales_order)
    if sales_order.status != 'picking':
        return HttpResponseForbidden("This sales order cannot be packed at this stage.")
    if request.method == 'POST':
        form = CollieProductForm(request.POST)
        if form.is_valid():
            collie_product = form.save(commit=False)
            collie_product.collie = collie
            collie_product.save()
            return redirect('add_collie_product', order_id=order_id, collie_id=collie_id)
    else:
        form = CollieProductForm()
        available_order_products = OrderProduct.objects.filter(order=sales_order)
        collie_products = CollieProduct.objects.filter(collie=collie)
    return render(request, 'warehouse/add_collie_product.html', {
        'form': form,
        'sales_order': sales_order,
        'collie': collie,
        'available_order_products': available_order_products,
        'collie_products': collie_products
    })

@login_required
def finalize_collie(request, order_id, collie_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to finalize collies.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    collie = get_object_or_404(Collie, id=collie_id, sales_order=sales_order)
    if sales_order.status != 'picking':
        return HttpResponseForbidden("This sales order cannot be packed at this stage.")
    if request.method == 'POST':
        form = CollieForm(request.POST, instance=collie)
        if form.is_valid():
            form.save()
            # Check if all products in the sales order are packed
            packed_quantities = {op.product.id: sum(cp.quantity for cp in op.collieproduct_set.all()) for op in sales_order.products.all()}
            order_quantities = {op.product.id: op.quantity for op in sales_order.products.all()}
            if packed_quantities == order_quantities:
                sales_order.status = 'packed'
                sales_order.save()
            return redirect('manage_warehouse')
    else:
        form = CollieForm(instance=collie)
    return render(request, 'warehouse/finalize_collie.html', {'form': form, 'sales_order': sales_order, 'collie': collie})

@login_required
def select_shipping_provider(request, order_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to select shipping providers.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    if sales_order.status != 'packed':
        return HttpResponseForbidden("This sales order cannot be shipped at this stage.")
    if request.method == 'POST':
        provider = request.POST.get('provider')
        if provider == 'easytrans':
            return export_sales_order(request, order_id)
        elif provider == 'sendcloud':
            return export_sales_order_to_sendcloud(request, order_id)
        elif provider == 'dummy':
            return create_dummy_shipping_label(request, order_id)
    return render(request, 'warehouse/select_shipping_provider.html', {'sales_order': sales_order})

@login_required
def confirm_shipment(request, order_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to confirm shipments.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    if sales_order.status != 'shipped':
        return HttpResponseForbidden("This sales order cannot be confirmed at this stage.")
    if request.method == 'POST':
        sales_order.status = 'delivered'
        sales_order.save()
        return redirect('manage_warehouse')
    return render(request, 'warehouse/confirm_shipment.html', {'sales_order': sales_order})

def generate_dummy_shipping_label():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Shipping Label")
    p.drawString(100, 730, "Order ID: 12345")
    p.drawString(100, 710, "Customer: John Doe")
    p.drawString(100, 690, "Address: 123 Main St, Amsterdam, NL")
    p.drawString(100, 670, "Tracking Number: ABC123XYZ")
    p.drawString(100, 650, "Weight: 10 kg")
    p.drawString(100, 630, "Dimensions: 100 x 50 x 30 cm")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

@login_required
def create_dummy_shipping_label(request, order_id):
    if request.user.role not in ['warehouse_manager', 'client_logistics_worker', 'client_fba_worker']:
        return HttpResponseForbidden("You do not have permission to create dummy shipping labels.")
    sales_order = get_object_or_404(SalesOrder, id=order_id, tenant=request.user.tenant)
    for collie in sales_order.collies.all():
        pdf_file = generate_dummy_shipping_label()
        collie.shipping_label.save(f"collie_{collie.id}_label.pdf", ContentFile(pdf_file.read()), save=True)
    sales_order.status = 'shipped'
    sales_order.save()
    messages.success(request, "Dummy shipping labels created successfully.")
    return redirect('manage_warehouse')