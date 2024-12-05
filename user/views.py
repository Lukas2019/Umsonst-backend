from os import read
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.response import Response
from yaml import serialize
from item.models import ShareCircle
from user.models import User, Complaint
from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from django.views.generic import TemplateView

from .serializers import MyUserSerializer, UserSerializer, ComplaintSerializer


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

class UserViewMe(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    def get_object(self):
        return self.request.user
    
class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(User, id=slug)
 
class ComplaintView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        share_circle_admin = ShareCircle.objects.filter(admin=self.request.user).all()
        return Complaint.objects.filter(user__post_circle__in=share_circle_admin).all()
    
class ComplaintReadView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Complaint, id=slug)
    
    def perform_update(self, serializer):
        serializer.read = True
        serializer.save()

class ComplaintCountView(generics.GenericAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def get(self, request):
        share_circle_admin = ShareCircle.objects.filter(admin=self.request.user).all()
        complaints = Complaint.objects.filter(user__post_circle__in=share_circle_admin).all()
        return Response({'count': complaints.count()})
    
class BlockUser(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, slug):
        user = get_object_or_404(User, id=slug)
        if user == request.user:
            raise ValidationError('You cannot block yourself')
        user.is_active = False
        user.save()
        return Response({'status': 'blocked'}, status=200)