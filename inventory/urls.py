from django.urls import path

from .views import login_page, logout_page
from inventory import views as user_views


urlpatterns = [
    path('register/', user_views.register, name='users-register'),
    path('login/', login_page, name='users-login'),
    path('logout/', logout_page, name='logout'),
]