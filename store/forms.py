from django import forms
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator
from django.contrib.auth import get_user_model
from .models import Season, Drop, Product, Order, Delivery

User = get_user_model()

class SupplierForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'name',
        'data-val': 'true',
        'data-val-required': 'Please enter name',
    }),
    min_length=2,
    max_length=100,
    error_messages={
            'required': 'Please enter your name',
            'min_length': 'Name must be at least 2 characters',
            'max_length': 'Name cannot exceed 100 characters',
        }
    )
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'address',
        'data-val': 'true',
        'data-val-required': 'Please enter address',
    }))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'data-val': 'true',
            'data-val-required': 'Please enter email',
        }),
        validators=[
            EmailValidator(message='Please enter a valid email address.')
        ]
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'data-val': 'true',
            'data-val-required': 'Please enter username',
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.',
            ),
            MinLengthValidator(4, message='Username must be at least 4 characters long.')
        ]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'data-val': 'true',
            'data-val-required': 'Please enter password',
        }),
        validators=[
            MinLengthValidator(8, message='Password must be at least 8 characters long.')
        ]
    )
    retype_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'id': 'retype_password',
        'data-val': 'true',
        'data-val-required': 'Please enter retype_password',
    }))
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        if name and not all(char.isalpha() or char.isspace() for char in name):
            raise forms.ValidationError("Name must contain only letters")
            
        return name.strip()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        retype_password = cleaned_data.get('retype_password')
        
        if password and retype_password and password != retype_password:
            self.add_error('retype_password', "Passwords don't match.")
        
        return cleaned_data


class BuyerForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'name',
        'data-val': 'true',
        'data-val-required': 'Please enter name',
    }),
    min_length=2,
    max_length=100,
    error_messages={
            'required': 'Please enter your name',
            'min_length': 'Name must be at least 2 characters',
            'max_length': 'Name cannot exceed 100 characters',
        }
    )
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'address',
        'data-val': 'true',
        'data-val-required': 'Please enter address',
    }))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'data-val': 'true',
            'data-val-required': 'Please enter email',
        }),
        validators=[
            EmailValidator(message='Please enter a valid email address.')
        ]
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'data-val': 'true',
            'data-val-required': 'Please enter username',
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.',
            ),
            MinLengthValidator(4, message='Username must be at least 4 characters long.')
        ]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'data-val': 'true',
            'data-val-required': 'Please enter password',
        }),
        validators=[
            MinLengthValidator(8, message='Password must be at least 8 characters long.')
        ]
    )
    retype_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'id': 'retype_password',
        'data-val': 'true',
        'data-val-required': 'Please enter retype_password',
    }))
    
    def clean_name(self):
        name = self.cleaned_data.get('name')

        if name and not all(char.isalpha() or char.isspace() for char in name):
            raise forms.ValidationError("Name must contain only letters")
            
        return name.strip()
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        retype_password = cleaned_data.get('retype_password')
        
        if password and retype_password and password != retype_password:
            self.add_error('retype_password', "Passwords don't match.")
        
        return cleaned_data


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'id': 'description'})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Season name cannot be empty.")
        
        # Check for duplicate names (excluding the current instance)
        if self.instance.pk:
            if Season.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A season with this name already exists.")
        else:
            if Season.objects.filter(name=name).exists():
                raise forms.ValidationError("A season with this name already exists.")
        
        return name


class DropForm(forms.ModelForm):
    class Meta:
        model = Drop
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Drop name cannot be empty.")
        
        # Check for duplicate names (excluding the current instance)
        if self.instance.pk:
            if Drop.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A drop with this name already exists.")
        else:
            if Drop.objects.filter(name=name).exists():
                raise forms.ValidationError("A drop with this name already exists.")
        
        return name


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sortno','price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
            'sortno': forms.NumberInput(attrs={'class': 'form-control', 'id': 'sortno'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'price'})
            
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Product name cannot be empty.")
        
        # Check for duplicate names (excluding the current instance)
        if self.instance.pk:
            if Product.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A product with this name already exists.")
        else:
            if Product.objects.filter(name=name).exists():
                raise forms.ValidationError("A product with this name already exists.")
        
        return name


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['supplier', 'product', 'design', 'color', 'buyer', 'season', 'quantity', 'drop']

        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control', 'id': 'supplier'}),
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'product'}),
            'design': forms.TextInput(attrs={'class': 'form-control', 'id': 'design'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'id': 'color'}),
            'buyer': forms.Select(attrs={'class': 'form-control', 'id': 'buyer'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity', 'min': 1}),
            'season': forms.Select(attrs={'class': 'form-control', 'id': 'season'}),
            'drop': forms.Select(attrs={'class': 'form-control', 'id': 'drop'}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = '__all__'

        widgets = {
            'order': forms.Select(attrs={'class': 'form-control', 'id': 'order'}),
            'courier_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'courier_name'}),
        }