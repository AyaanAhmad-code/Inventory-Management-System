from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from store.models import Stock
import requests  # For device notifications

def check_low_stock_and_alert(threshold=10):
    low_stocks = Stock.objects.filter(quantity__lt=threshold)
    
    if low_stocks.exists():
        # Prepare email content
        context = {
            'low_stocks': low_stocks,
            'threshold': threshold
        }
        email_body = render_to_string('inventory/emails/low_stock_alert.html', context)
        email_subject = f'Low Stock Alert: {low_stocks.count()} items below threshold'
        
        # Send email to admins
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            ['admin1@example.com', 'admin2@example.com'],  # Add recipient emails
            html_message=email_body,
            fail_silently=False
        )
        
        # Send device notifications
        send_device_notifications(low_stocks)

def send_device_notifications(low_stocks):
    # For mobile apps (using Firebase Cloud Messaging)
    fcm_api_key = "your-fcm-server-key"
    fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    # For web push notifications (using service workers)
    web_push_payload = {
        "notification": {
            "title": "Low Stock Alert",
            "body": f"{len(low_stocks)} items are below threshold",
            "icon": "/static/images/alert-icon.png"
        }
    }
    
    # Example: Send to FCM (Android/iOS)
    headers = {
        "Authorization": f"key={fcm_api_key}",
        "Content-Type": "application/json"
    }
    
    for stock in low_stocks:
        payload = {
            "to": "/topics/low_stock",  # Or specific device tokens
            "data": {
                "title": "Low Stock Alert",
                "message": f"{stock.product.name} is low (Qty: {stock.quantity})",
                "stock_id": str(stock.id),
                "type": "low_stock"
            }
        }
        
        try:
            response = requests.post(fcm_url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send FCM notification: {e}")