# Generated by Django 5.1 on 2025-04-27 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_remove_product_stock_product_total_stock_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='last_alert_sent',
        ),
        migrations.RemoveField(
            model_name='product',
            name='low_stock_threshold',
        ),
        migrations.RemoveField(
            model_name='product',
            name='total_stock',
        ),
        migrations.DeleteModel(
            name='LowStockNotification',
        ),
    ]
