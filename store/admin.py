from django.contrib import admin
from django.contrib import messages
from store.models import Report, ReportItem

from .models import (
    Supplier,
    Buyer,
    Season,
    Drop,
    Product,
    Order,
    Delivery,
)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'address', 'created_date']

class BuyerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'address', 'created_date']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'supplier', 'buyer', 'quantity', 'status')
    list_editable = ('status',)
    actions = ['complete_orders']
    list_filter = ('status', 'supplier', 'product')
    search_fields = ('product__name', 'supplier__name', 'buyer__name')
    
    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = Order.objects.get(pk=obj.pk).status
        
        super().save_model(request, obj, form, change)
        
        # If status changed to Completed, reduce stock
        if change and old_status != 'Completed' and obj.status == 'Completed':
            try:
                obj.reduce_stock()
                messages.success(request, f"Order #{obj.id} completed and stock updated")
            except Exception as e:
                messages.error(request, f"Failed to update stock: {str(e)}")
                # Revert status if needed
                obj.status = old_status
                obj.save()

    def complete_orders(self, request, queryset):
        for order in queryset:
            if order.status != 'Completed':
                try:
                    order.status = 'Completed'
                    order.save()  # This will trigger reduce_stock()
                    messages.success(request, f"Order #{order.id} completed")
                except Exception as e:
                    messages.error(request, f"Failed to complete order #{order.id}: {str(e)}")
    complete_orders.short_description = "Mark selected orders as completed"



class ReportItemInline(admin.TabularInline):
    model = ReportItem
    extra = 0
    readonly_fields = ('product', 'supplier', 'quantity', 'value', 'details')
    can_delete = False

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_at')
    list_filter = ('report_type', 'generated_at')
    search_fields = ('title', 'notes')
    inlines = [ReportItemInline]
    readonly_fields = ('generated_at',)
    
    def has_add_permission(self, request):
        return False

@admin.register(ReportItem)
class ReportItemAdmin(admin.ModelAdmin):
    list_display = ('report', 'product', 'quantity', 'value')
    list_filter = ('report__report_type',)
    search_fields = ('product__name', 'supplier__name')
    
    def has_add_permission(self, request):
        return False

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Season)
admin.site.register(Drop)
admin.site.register(Product)
admin.site.register(Delivery)
admin.site.register(Order, OrderAdmin)