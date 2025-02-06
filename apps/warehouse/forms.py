from django import forms
from .models import SalesOrder, OrderProduct, Product, Customer, SalesOrderDocument, Collie, CollieProduct
from apps.crm.models import Consignee

class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'is_fba_shipment', 'shipping_label']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Consignee.objects.filter(tenant=self.instance.tenant) if self.instance.tenant else Consignee.objects.none()

class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'asin_sticker']

class SalesOrderDocumentForm(forms.ModelForm):
    class Meta:
        model = SalesOrderDocument
        fields = ['document']

class CollieForm(forms.ModelForm):
    class Meta:
        model = Collie
        fields = ['dimensions', 'weight']

class CollieProductForm(forms.ModelForm):
    class Meta:
        model = CollieProduct
        fields = ['order_product', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'order_id' in kwargs['initial']:
            order_id = kwargs['initial']['order_id']
            self.fields['order_product'].queryset = OrderProduct.objects.filter(order_id=order_id)
        else:
            self.fields['order_product'].queryset = OrderProduct.objects.none()