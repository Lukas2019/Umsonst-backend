from django.urls import path, include
from .views import (
    UserCreate,
    SetPassword
)
import django_rest_passwordreset

urlpatterns = [
    path('register/', UserCreate.as_view()),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_reset/<str:token>/', SetPassword.as_view(), name='password_reset_change'),
    ]
