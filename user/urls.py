from django.urls import path, include
from pyparsing import C
from .views import (
    UserCreate,
    SetPassword,
    UserViewMe,
    UserView,
    ComplaintView,
    BlockUser,
    ComplaintReadView,
    ComplaintCountView,
    SetPasswordView
)
import django_rest_passwordreset

app_name = 'user'

urlpatterns = [
    path('register/', UserCreate.as_view(), name='register'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_reset/<str:token>/', SetPassword.as_view(), name='password_reset_change'),
    path('set-password/', SetPasswordView.as_view(), name='password_change'),
    path('me/', UserViewMe.as_view(),name='my-user'),
    path('complaint/', ComplaintView.as_view(), name='complaint'),
    path('complaint/count/', ComplaintCountView.as_view(), name='complaint-count'),
    path('complaint/<slug:slug>/', ComplaintReadView.as_view(), name='complaint-detail'),
    path('<slug:slug>/block/', BlockUser.as_view(), name='complaint-detail'),
    path('<slug:slug>/', UserView.as_view(), name='user' ),
    ]
