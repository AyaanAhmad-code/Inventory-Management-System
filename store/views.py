from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, F, Q
import csv
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

from inventory.models import User
from .models import (
    Stock,
    Supplier,
    Buyer,
    Season,
    Drop,
    Product,
    Order,
    Delivery,
    Alert,
)
from .forms import (
    SupplierForm,
    BuyerForm,
    SeasonForm,
    DropForm,
    ProductForm,
    OrderForm,
    DeliveryForm
)

def stock_list(request):
    stocks = Stock.objects.all().order_by('-date_added')
    return render(request, 'store/stock_list.html', {'stocks': stocks})

def add_stock(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        supplier_id = request.POST.get('supplier')
        quantity = int(request.POST.get('quantity', 0))
        
        product = get_object_or_404(Product, id=product_id)
        supplier = get_object_or_404(Supplier, id=supplier_id)
        
        stock, created = Stock.objects.get_or_create(
            product=product,
            supplier=supplier,
            defaults={'quantity': quantity}
        )
        
        if not created:
            stock.quantity += quantity
            stock.save()
        
        messages.success(request, f'Added {quantity} units of {product.name} to stock')
        return redirect('stock_list')
    
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'store/add_stock.html', {
        'products': products,
        'suppliers': suppliers
    })

def update_stock(request, pk):
    stock = get_object_or_404(Stock, id=pk)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 0))
        stock.quantity = new_quantity
        stock.save()
        messages.success(request, 'Stock updated successfully')
        return redirect('stock_list')
    
    return render(request, 'store/update_stock.html', {'stock': stock})

def low_stock(request, threshold=10):
    low_stocks = Stock.objects.filter(quantity__lt=threshold).order_by('quantity')
    return render(request, 'store/low_stock.html', {
        'stocks': low_stocks,
        'threshold': threshold
    })

def complete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status != 'Completed':
        try:
            order.status = 'Completed'
            order.save()
            messages.success(request, f'Order #{order.id} completed and stock updated')
        except ValueError as e:
            messages.error(request, f'Could not complete order: {e}')
    return redirect('order_detail', pk=order.id)
@login_required
def alert_list(request):
    alerts = Alert.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'alerts/list.html', {'alerts': alerts})

@login_required
def mark_alert_read(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    alert.is_read = True
    alert.save()
    return redirect('alert_list')
# Supplier views
@login_required(login_url='login')
def create_supplier(request):
    forms = SupplierForm()
    if request.method == 'POST':
        forms = SupplierForm(request.POST)
        if forms.is_valid():
            name = forms.cleaned_data['name']
            address = forms.cleaned_data['address']
            email = forms.cleaned_data['email']
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            retype_password = forms.cleaned_data['retype_password']
            if password == retype_password:
                user = User.objects.create_user(username=username, password=password, email=email, is_supplier=True)
                Supplier.objects.create(user=user, name=name, address=address)
                messages.success(request, 'Supplier registered successfully!')
                return redirect('supplier-list')
            else:
            # Form is invalid, errors will be available in the template
                messages.error(request, 'Please correct the errors below.')
        else:
             form = SupplierForm()
    context = {
        'form': forms
    }
    return render(request, 'store/addSupplier.html', context)


class SupplierListView(ListView):
    model = Supplier
    template_name = 'store/supplier_list.html'
    context_object_name = 'supplier'

@login_required
def search_view(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search across multiple models
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(sortno__icontains=query)
        )
        
        orders = Order.objects.filter(
            Q(product__name__icontains=query) |
            Q(design__icontains=query) |
            Q(color__icontains=query) |
            Q(buyer__name__icontains=query)
        )
        
        suppliers = Supplier.objects.filter(name__icontains=query)
        buyers = Buyer.objects.filter(name__icontains=query)
        
        results = {
            'products': products,
            'orders': orders,
            'suppliers': suppliers,
            'buyers': buyers,
            'query': query
        }
    
    return render(request, 'store/search_results.html', results)
# Product Detail
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# Supplier Detail
@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'store/supplier_detail.html', {'supplier': supplier})

# Buyer Detail
@login_required
def buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    return render(request, 'store/buyer_detail.html', {'buyer': buyer})

# Order Detail
@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'store/order_detail.html', {'order': order})
# Buyer views
@login_required(login_url='login')
def create_buyer(request):
    forms = BuyerForm()
    if request.method == 'POST':
        forms = BuyerForm(request.POST)
        if forms.is_valid():
            name = forms.cleaned_data['name']
            address = forms.cleaned_data['address']
            email = forms.cleaned_data['email']
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            retype_password = forms.cleaned_data['retype_password']
            if password == retype_password:
                user = User.objects.create_user(username=username, password=password, email=email, is_buyer=True)
                Buyer.objects.create(user=user, name=name, address=address)
                messages.success(request, 'Buyer registered successfully!')
                return redirect('buyer-list')
            else:
            # Form is invalid, errors will be available in the template
                messages.error(request, 'Please correct the errors below.')
        else:
            form = BuyerForm()
    context = {
        'form': forms
    }
    return render(request, 'store/addbuyer.html', context)

class BuyerListView(ListView):
    model = Buyer
    template_name = 'store/buyer_list.html'
    context_object_name = 'buyer'


# Season views
@login_required(login_url='login')
def create_season(request):
    forms = SeasonForm()
    if request.method == 'POST':
        forms = SeasonForm(request.POST)
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Season created successfully!')
            return redirect('season-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SeasonForm()
    context = {
        'form': forms
    }
    return render(request, 'store/addSeason.html', context)


class SeasonListView(ListView):
    model = Season
    template_name = 'store/season_list.html'
    context_object_name = 'season'


# Drop views
@login_required(login_url='login')
def create_drop(request):
    forms = DropForm()
    if request.method == 'POST':
        forms = DropForm(request.POST)
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Drop created successfully!')
            return redirect('drop-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DropForm()
    context = {
        'form': forms
    }
    return render(request, 'store/addCategory.html', context)


class DropListView(ListView):
    model = Drop
    template_name = 'store/category_list.html'
    context_object_name = 'drop'


# Product views
@login_required(login_url='login')
def create_product(request):
    forms = ProductForm()
    if request.method == 'POST':
        forms = ProductForm(request.POST)
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    context = {
        'form': forms
    }
    return render(request, 'store/addProduct.html', context)


class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'product'


# Order views
@login_required(login_url='login')
def create_order(request):
    forms = OrderForm()
    if request.method == 'POST':
        forms = OrderForm(request.POST)
        if forms.is_valid():
            supplier = forms.cleaned_data['supplier']
            product = forms.cleaned_data['product']
            design = forms.cleaned_data['design']
            color = forms.cleaned_data['color']
            buyer = forms.cleaned_data['buyer']
            quantity = forms.cleaned_data['quantity']
            season = forms.cleaned_data['season']

            drop = forms.cleaned_data['drop']
            Order.objects.create(
                supplier=supplier,
                product=product,
                design=design,
                color=color,
                buyer=buyer,
                season=season,
                quantity=quantity,
                drop=drop,
                status='pending'
            )
            messages.success(request, 'Order created successfully!')
            return redirect('order-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OrderForm()
    context = {
        'form': forms
    }
    return render(request, 'store/addOrder.html', context)


class OrderListView(ListView):
    model = Order
    template_name = 'store/order_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.all().order_by('-id')
        return context
    
# Delivery views
@login_required(login_url='login')
def create_delivery(request):
    forms = DeliveryForm()
    if request.method == 'POST':
        forms = DeliveryForm(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('delivery-list')
    context = {
        'form': forms
    }
    return render(request, 'store/addelivery.html', context)


class DeliveryListView(ListView):
    model = Delivery
    template_name = 'store/delivery_list.html'
    context_object_name = 'delivery'

def test_order_completion(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        order.status = 'Completed'
        order.save()
        return JsonResponse({
            'success': True,
            'message': f'Order {order_id} completed',
            'stock_reduced': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
def report_list(request):
    from store.models import Report
    reports = Report.objects.all().order_by('-generated_at')
    return render(request, 'store/report_list.html', {'reports': reports})

def generate_stock_report(request):
    from store.models import Product, Report, ReportItem
    products = Product.objects.annotate(
        total_quantity=Sum('stock__quantity'),
        total_value=Sum(F('stock__quantity') * F('price'))
    ).filter(total_quantity__gt=0)
    
    report = Report.objects.create(
        report_type='stock',
        title=f"Stock Report - {timezone.now().strftime('%Y-%m-%d')}",
        notes="Current inventory stock levels"
    )
    
    for product in products:
        ReportItem.objects.create(
            report=report,
            product=product,
            quantity=product.total_quantity,
            value=product.total_value or 0,
            details={
                'product_name': product.name,
                'unit_price': float(product.price)
            }
        )
    
    messages.success(request, "Stock report generated successfully")
    return redirect('report_list')

def generate_sales_report(request):
    from store.models import Order, Report, ReportItem
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        orders = Order.objects.filter(
            status='Completed',
            order_date__gte=start_date,
            order_date__lte=end_date
        ).select_related('product', 'supplier', 'buyer')
        
        report = Report.objects.create(
            report_type='sales',
            title=f"Sales Report {start_date} to {end_date}",
            start_date=start_date,
            end_date=end_date,
            notes=f"Sales report from {start_date} to {end_date}"
        )
        
        for order in orders:
            ReportItem.objects.create(
                report=report,
                product=order.product,
                supplier=order.supplier,
                quantity=order.quantity,
                value=order.quantity * order.product.price,
                details={
                    'order_id': order.id,
                    'buyer': order.buyer.name,
                    'date': order.order_date.strftime('%Y-%m-%d')
                }
            )
        
        messages.success(request, "Sales report generated successfully")
        return redirect('report_list')
    
    default_end = timezone.now().date()
    default_start = default_end - timedelta(days=30)
    return render(request, 'store/sales_report_form.html', {
        'default_start': default_start,
        'default_end': default_end
    })

def export_report_csv(request, report_id):
    from store.models import Report
    report = Report.objects.get(pk=report_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.title}.csv"'
    
    writer = csv.writer(response)
    
    if report.report_type == 'stock':
        writer.writerow(['Product', 'Quantity', 'Unit Price', 'Total Value'])
        for item in report.items.all():
            writer.writerow([
                item.product.name,
                item.quantity,
                item.product.price,
                item.value
            ])
    elif report.report_type == 'sales':
        writer.writerow(['Order Date', 'Product', 'Quantity', 'Unit Price', 'Total', 'Buyer'])
        for item in report.items.all():
            writer.writerow([
                item.details.get('date'),
                item.product.name,
                item.quantity,
                item.product.price,
                item.value,
                item.details.get('buyer')
            ])
    
    return response