from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from inventory.models import User
from django.contrib.auth import get_user_model


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, unique=True)
    address = models.CharField(max_length=220)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, unique=True)
    address = models.CharField(max_length=220)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

User = get_user_model()

class Alert(models.Model):
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('order_completed', 'Order Completed'),
        ('inventory_update', 'Inventory Update'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_content_type = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.user.username}"
    
class Season(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=220)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Drop(models.Model):
    name = models.CharField(max_length=120, unique=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120, unique=True)
    sortno = models.PositiveIntegerField()
    created_date = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('decline', 'Decline'),
        ('complete', 'Complete'),
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    design = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, null=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True)
    drop = models.ForeignKey(Drop, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1,verbose_name="Order Quantity",
        help_text="Number of items ordered")
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='Pending')
    created_date = models.DateField(auto_now_add=True)
    order_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # First save the order to ensure we have a PK
        super().save(*args, **kwargs)
        
        # If status changed to Completed, reduce stock
        if self.status == 'Completed':
            self.reduce_stock()

    def reduce_stock(self):
        print(f"Attempting to reduce stock for order {self.id}")  # Debugging
        try:
            with transaction.atomic():
                # Use select_for_update() to lock the stock record
                stock = Stock.objects.select_for_update().get(
                    product=self.product, 
                    supplier=self.supplier
                )
                print(f"Current stock: {stock.quantity}, Order qty: {self.quantity}")
                
                if stock.quantity >= self.quantity:
                    stock.quantity -= self.quantity
                    stock.save()
                    print(f"Stock reduced to {stock.quantity}")
                else:
                    print(f"Insufficient stock! Available: {stock.quantity}, Needed: {self.quantity}")
        except Stock.DoesNotExist:
            print(f"No stock record for {self.product} from {self.supplier}")
        except Exception as e:
            print(f"Error reducing stock: {str(e)}")

@receiver(post_save, sender=Order)
def update_stock_on_order_completion(sender, instance, created, **kwargs):
    if instance.status == 'Completed':
        print(f"Signal triggered for order {instance.id}")
        instance.reduce_stock()

class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    courier_name = models.CharField(max_length=120)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.courier_name
    
class Stock(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE,)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_added = models.DateField(auto_now_add=True)
    alert_threshold = models.IntegerField(default=10)
    
    @property
    def is_low(self):
        return self.quantity < self.alert_threshold
    
    class Meta:
        unique_together = ('product', 'supplier')

    def __str__(self):
        return f"{self.product} - {self.quantity} units"

# Example of a stock history model
class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='history')
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_date = models.DateTimeField(auto_now_add=True)
    change_reason = models.CharField(max_length=255, blank=True)
    class Meta:
        ordering = ['-change_date']
    
    def __str__(self):
        return f"{self.stock.product} changed from {self.previous_quantity} to {self.new_quantity}"

class Report(models.Model):
    REPORT_TYPES = [
        ('stock', 'Stock Report'),
        ('sales', 'Sales Report'),
        ('purchase', 'Purchase Report'),
        ('low_stock', 'Low Stock Alert'),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=100)
    generated_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    file = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"

class ReportItem(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.report.title} - {self.product.name if self.product else 'N/A'}"   