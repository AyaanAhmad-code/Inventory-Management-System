# Generated by Django 5.1 on 2025-04-27 07:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_product_last_alert_sent_product_low_stock_threshold_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.AddField(
            model_name='product',
            name='total_stock',
            field=models.IntegerField(default=0, help_text='Total available quantity across all suppliers'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
        migrations.CreateModel(
            name='LowStockNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_dismissed', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_notifications', to='store.product')),
            ],
            options={
                'verbose_name': 'Low Stock Notification',
                'verbose_name_plural': 'Low Stock Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.DeleteModel(
            name='Alert',
        ),
    ]
