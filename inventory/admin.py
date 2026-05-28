from django.contrib import admin
from .models import (
    Category, Product, ProductUnit, ProductStock,
    Sale, SaleItem, Payment, Purchase, PurchaseItem,
    TransferBatch, StockTransfer, Supplier, RetailStock,
    RetailSale, PurchaseOrder, PurchaseOrderItem,
    SaleOrder, SaleOrderItem, CompanyDetails, StockTake, StockTakeItem
)

# ==================== CATEGORY ====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']

# ==================== PRODUCT ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sku', 'base_unit', 'cost_price', 'selling_price', 'total_stock']
    search_fields = ['name', 'sku']
    list_filter = ['category']

# ==================== PRODUCT UNIT ====================
@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'unit_name', 'quantity_in_base', 'selling_price', 'is_default', 'is_active']
    list_filter = ['unit_name', 'is_default', 'is_active']
    search_fields = ['product__name', 'unit_name']

# ==================== PRODUCT STOCK ====================
@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'location', 'quantity']
    list_filter = ['location']
    search_fields = ['product__name']

# ==================== SALE ====================
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'document_number', 'customer', 'total_amount', 'document_status', 'date']
    list_filter = ['document_status', 'document_type']
    search_fields = ['document_number', 'customer__name']
    raw_id_fields = ['customer', 'location', 'created_by']

# ==================== SALE ITEM ====================
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale', 'product', 'quantity', 'unit_name', 'unit_price', 'total_price']
    search_fields = ['product__name', 'sale__document_number']
    list_filter = ['unit_name']

# ==================== PAYMENT ====================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method']
    search_fields = ['sale__document_number']

# ==================== PURCHASE ====================
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference', 'supplier_name', 'location', 'total_amount', 'purchase_date']
    list_filter = ['supplier_name', 'location']
    search_fields = ['reference', 'supplier_name']

@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'purchase', 'product', 'quantity', 'unit_price']
    search_fields = ['product__name', 'purchase__reference']

# ==================== TRANSFERS ====================
@admin.register(TransferBatch)
class TransferBatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference', 'from_location', 'to_location', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['reference']

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'status', 'batch', 'transfer_date']
    list_filter = ['status']
    search_fields = ['product__name', 'batch__reference']

# ==================== SUPPLIER ====================
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']

# ==================== RETAIL ====================
@admin.register(RetailStock)
class RetailStockAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'location', 'quantity']
    list_filter = ['location']
    search_fields = ['product__name']

@admin.register(RetailSale)
class RetailSaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'amount_given', 'quantity_given', 'sale_date']
    list_filter = ['location']
    search_fields = ['product__name']

# ==================== PURCHASE ORDER ====================
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference', 'supplier_name', 'status', 'order_date']
    list_filter = ['status']
    search_fields = ['reference', 'supplier_name']

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'purchase_order', 'product', 'quantity', 'unit_price']
    search_fields = ['product__name', 'purchase_order__reference']

# ==================== SALE ORDER ====================
@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference', 'customer', 'status', 'sale_date']
    list_filter = ['status']
    search_fields = ['reference', 'customer__name']

@admin.register(SaleOrderItem)
class SaleOrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale_order', 'product', 'quantity', 'unit_price']
    search_fields = ['product__name', 'sale_order__reference']

# ==================== COMPANY DETAILS ====================
@admin.register(CompanyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'email']
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'address', 'phone', 'email', 'website', 'logo', 'tax_id')
        }),
        ('Bank Information', {
            'fields': ('bank_name', 'bank_account', 'bank_branch')
        }),
        ('Document Settings', {
            'fields': ('invoice_prefix', 'quotation_prefix', 'receipt_prefix', 'invoice_footer', 'quotation_footer')
        }),
    )

# ==================== STOCK TAKE ====================
@admin.register(StockTake)
class StockTakeAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference', 'location', 'status', 'start_date']
    list_filter = ['status']
    search_fields = ['reference', 'location__name']

@admin.register(StockTakeItem)
class StockTakeItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock_take', 'product', 'quantity_on_hand', 'quantity_counted', 'variance']
    search_fields = ['product__name', 'stock_take__reference']

# ==================== ADMIN SITE HEADER ====================
admin.site.site_header = "Tusakimu Enterprises - Inventory Management"
admin.site.site_title = "Tusakimu Inventory Admin"
admin.site.index_title = "Tusakimu Enterprises Administration"
