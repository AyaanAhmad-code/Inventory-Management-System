from django.test import TestCase
from .models import Stock, Product, Supplier, User , Alert

class AlertSignalTests(TestCase):
    def test_low_stock_alert(self):
        user = User.objects.create(username='admin', is_admin=True)
        product = Product.objects.create(name='Test Product')
        supplier = Supplier.objects.create(user=user, name='Test Supplier', address='Test')
        
        # Create stock below threshold
        stock = Stock.objects.create(
            product=product,
            supplier=supplier,
            quantity=5,  # Below default threshold of 10
            alert_threshold=10
        )
        
        # Verify alert was created
        self.assertEqual(Alert.objects.count(), 1)