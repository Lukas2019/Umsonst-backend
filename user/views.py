from django.urls import reverse
from user.models import User
from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from django.views.generic import TemplateView

from .serializers import MyUserSerializer, UserSerializer


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class SetPassword(TemplateView):
    template_name = 'reset_password.html'

    def get_context_data(self, **kwargs):
        context = {}
        context = super().get_context_data(**kwargs)
        #context['token'] = self.request.GET.get('token')
        context['url'] = reverse('user:password_reset:reset-password-confirm')
        return context

class UserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    def get_object(self):
        return self.request.user
