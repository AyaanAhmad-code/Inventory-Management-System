from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from inventory.models import User 
from django.contrib.auth.forms import UserCreationForm

class CreateUserForm(UserCreationForm):
    """Form for creating a new user with an email field."""
    email = forms.EmailField()

    class Meta:
        """Meta options for the CreateUserForm."""
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.',
                code='invalid_username'
            ),
        ],
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        min_length=8,
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check minimum length
        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters long.")
            
        # Check if username exists (for login form, username should exist)
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username does not exist.")
            
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        username = self.cleaned_data.get('username')
        
        # If username is valid and exists
        if username and not self._errors.get('username'):
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid password for this username.")
        
        return password