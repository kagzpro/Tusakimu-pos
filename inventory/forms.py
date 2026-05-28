import json
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Product, ProductStock, ProductUnit,
    RetailSale, RetailStock, Sale, SaleItem, Payment,
    Purchase, PurchaseItem, TransferBatch, StockTransfer,
    PurchaseOrder, PurchaseOrderItem, SaleOrder, SaleOrderItem,
    CompanyDetails, Category, Supplier
)
from core.models import Location
from transactions.models import Customer


# ==================== PRODUCT FORM ====================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'base_unit', 'cost_price', 'selling_price', 'reorder_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'base_unit': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('piece', 'Piece (pc)'),
                ('kilogram', 'Kilogram (kg)'),
                ('gram', 'Gram (g)'),
                ('liter', 'Liter (L)'),
                ('milliliter', 'Milliliter (ml)'),
                ('meter', 'Meter (m)'),
                ('centimeter', 'Centimeter (cm)'),
            ]),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ==================== PRODUCT UNIT FORM ====================
class ProductUnitForm(forms.ModelForm):
    class Meta:
        model = ProductUnit
        fields = ['product', 'unit_name', 'quantity_in_base', 'selling_price', 'is_default', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control select2'}),
            'unit_name': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('piece', 'Piece (pc)'),
                ('packet', 'Packet (pkt)'),
                ('carton', 'Carton (ctn)'),
                ('box', 'Box (box)'),
                ('dozen', 'Dozen (doz)'),
                ('gross', 'Gross (gr)'),
                ('roll', 'Roll (roll)'),
                ('bundle', 'Bundle (bdl)'),
                ('set', 'Set (set)'),
                ('pair', 'Pair (pr)'),
                ('bag', 'Bag (bag)'),
                ('bottle', 'Bottle (btl)'),
            ]),
            'quantity_in_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ==================== PRODUCT STOCK FORM ====================
class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ['product', 'location', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control select2'}),
            'location': forms.Select(attrs={'class': 'form-control select2'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['location'].initial = self.user.profile.assigned_location


# ==================== RETAIL SALE FORM ====================
class RetailSaleForm(forms.ModelForm):
    current_stock = forms.DecimalField(
        required=False,
        decimal_places=2,
        disabled=True,
        label="Available Stock",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    class Meta:
        model = RetailSale
        fields = ['product', 'location', 'amount_given', 'unit_price', 'current_stock']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control select2'}),
            'location': forms.Select(attrs={'class': 'form-control select2'}),
            'amount_given': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['product'].queryset = Product.objects.all()
        
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['location'].initial = self.user.profile.assigned_location
        
        if self.instance and self.instance.pk:
            try:
                stock = ProductStock.objects.get(
                    product=self.instance.product,
                    location=self.instance.location
                )
                self.fields['current_stock'].initial = stock.quantity
            except ProductStock.DoesNotExist:
                self.fields['current_stock'].initial = 0

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        location = cleaned_data.get('location')
        amount_given = cleaned_data.get('amount_given')
        unit_price = cleaned_data.get('unit_price')

        if product and location:
            try:
                main_stock = ProductStock.objects.get(product=product, location=location)
                
                if amount_given and unit_price and unit_price > 0:
                    quantity_needed = amount_given / unit_price
                    
                    if main_stock.quantity < quantity_needed:
                        self.add_error(
                            'amount_given',
                            f"Insufficient stock. Available: {main_stock.quantity:.2f} units. "
                            f"Required: {quantity_needed:.2f} units for UGX {amount_given:.2f}"
                        )
                
                self.cleaned_data['current_stock'] = main_stock.quantity
                
            except ProductStock.DoesNotExist:
                self.add_error('product', "No stock available for this product at selected location")
                self.cleaned_data['current_stock'] = 0

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user:
            instance.sold_by = self.user
        
        if instance.amount_given and instance.unit_price:
            instance.quantity_given = instance.amount_given / instance.unit_price
        
        if commit:
            instance.save()
        
        return instance


# ==================== RETAIL STOCK TRANSFER FORM ====================
class RetailStockTransferForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'})
    )
    transfer_type = forms.ChoiceField(
        choices=[
            ('TO_RETAIL', 'Transfer to Retail'),
            ('TO_MAIN', 'Return to Main Inventory')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['location'].initial = self.user.profile.assigned_location

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        location = cleaned_data.get('location')
        quantity = cleaned_data.get('quantity')
        transfer_type = cleaned_data.get('transfer_type')

        if product and location and quantity:
            try:
                main_stock = ProductStock.objects.get(product=product, location=location)
                retail_stock, _ = RetailStock.objects.get_or_create(product=product, location=location)

                if transfer_type == 'TO_RETAIL' and main_stock.quantity < quantity:
                    self.add_error('quantity', f"Not enough stock in main inventory. Available: {main_stock.quantity}")
                elif transfer_type == 'TO_MAIN' and retail_stock.quantity < quantity:
                    self.add_error('quantity', f"Not enough stock in retail. Available: {retail_stock.quantity}")

            except ProductStock.DoesNotExist:
                self.add_error('product', "No stock available for this product at selected location")

        return cleaned_data


# ==================== SALE FORM (SIMPLIFIED - NO ITEMS VALIDATION) ====================
# ==================== SALE FORM (SIMPLIFIED - NO ITEMS VALIDATION) ====================
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['document_type', 'customer', 'location', 'paid_amount', 'date', 'due_date', 'currency', 'notes', 'terms']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'location': forms.Select(attrs={'class': 'form-control select2'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'currency': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('UGX', 'UGX - Ugandan Shilling'),
            ]),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set customer queryset
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['customer'].required = False
        self.fields['customer'].empty_label = "Select Customer"
        
        # Set location queryset
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        self.fields['location'].required = True
        
        # Set currency default - CRITICAL FIX
        self.fields['currency'].initial = 'UGX'
        self.fields['currency'].required = True
        self.fields['currency'].empty_label = None
        
        # Set initial dates
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now()
            self.fields['due_date'].initial = timezone.now().date() + timezone.timedelta(days=30)

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        customer = cleaned_data.get('customer')
        
        # Set currency if not provided
        if not cleaned_data.get('currency'):
            cleaned_data['currency'] = 'UGX'
        
        # Only validate customer for invoices
        if document_type == 'invoice' and not customer:
            raise ValidationError("Customer is required for invoices.")
        
        return cleaned_data

# ==================== PAYMENT FORM ====================
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'payment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.sale = kwargs.pop('sale', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.sale:
            max_amount = self.sale.balance_due
            self.fields['amount'].widget.attrs['max'] = max_amount
            self.fields['amount'].help_text = f'Balance due: UGX {max_amount:.2f}'

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.sale and amount > self.sale.balance_due:
            raise ValidationError(f"Payment amount cannot exceed balance due of UGX {self.sale.balance_due:.2f}")
        return amount

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.sale:
            instance.sale = self.sale
        if self.user:
            instance.received_by = self.user
        
        if commit:
            instance.save()
        return instance


# ==================== SALE PAYMENT FORM (SIMPLIFIED) ====================
class SalePaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'payment_date', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_date'].initial = timezone.now().date()


# ==================== PURCHASE FORM ====================
class PurchaseForm(forms.ModelForm):
    items_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='[]'
    )
    
    class Meta:
        model = Purchase
        fields = ['supplier_name', 'location', 'purchase_date', 'notes']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control select2'}),
            'purchase_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['location'].initial = self.user.profile.assigned_location
        
        if not self.instance.pk:
            self.fields['purchase_date'].initial = timezone.now()


# ==================== TRANSFER FORM ====================
class TransferForm(forms.ModelForm):
    items_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='[]'
    )
    
    class Meta:
        model = TransferBatch
        fields = ['from_location', 'to_location', 'transfer_date', 'notes']
        widgets = {
            'from_location': forms.Select(attrs={'class': 'form-control select2'}),
            'to_location': forms.Select(attrs={'class': 'form-control select2'}),
            'transfer_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.locations is not None:
            self.fields['from_location'].queryset = self.locations
            self.fields['to_location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['from_location'].initial = self.user.profile.assigned_location
        
        if not self.instance.pk:
            self.fields['transfer_date'].initial = timezone.now()

    def clean(self):
        cleaned_data = super().clean()
        from_location = cleaned_data.get('from_location')
        to_location = cleaned_data.get('to_location')
        
        if from_location and to_location and from_location == to_location:
            raise ValidationError("Source and destination locations cannot be the same.")
        
        return cleaned_data


# ==================== PURCHASE ORDER FORM ====================
class PurchaseOrderForm(forms.ModelForm):
    items_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='[]'
    )
    
    class Meta:
        model = PurchaseOrder
        fields = ['supplier_name', 'location', 'order_date', 'expected_date', 'notes']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control select2'}),
            'order_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expected_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['location'].initial = self.user.profile.assigned_location
        
        if not self.instance.pk:
            self.fields['order_date'].initial = timezone.now()
            self.fields['expected_date'].initial = timezone.now().date() + timezone.timedelta(days=7)


# ==================== SALE ORDER FORM ====================
class SaleOrderForm(forms.ModelForm):
    items_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='[]'
    )
    
    class Meta:
        model = SaleOrder
        fields = ['customer', 'location', 'sale_date', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'location': forms.Select(attrs={'class': 'form-control select2'}),
            'sale_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.locations = kwargs.pop('locations', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['customer'].queryset = Customer.objects.all()
        
        if self.locations is not None:
            self.fields['location'].queryset = self.locations
        
        if self.user and hasattr(self.user, 'profile'):
            if not self.user.profile.can_access_all_locations and self.user.profile.assigned_location:
                self.fields['location'].initial = self.user.profile.assigned_location
        
        if not self.instance.pk:
            self.fields['sale_date'].initial = timezone.now()


# ==================== COMPANY DETAILS FORM ====================
class CompanyDetailsForm(forms.ModelForm):
    class Meta:
        model = CompanyDetails
        fields = [
            'name', 'address', 'phone', 'email', 'website', 'tax_id',
            'bank_name', 'bank_account', 'bank_branch', 'logo',
            'invoice_prefix', 'quotation_prefix', 'receipt_prefix',
            'invoice_footer', 'quotation_footer'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_branch': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'quotation_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_footer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quotation_footer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }