from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth import get_user_model
import uuid
from django import forms
import random
#Users = get_user_model()

class MyAccountManager(BaseUserManager):
    def create_user(self, fullname=None, birthday=None, zipcode=None,password=None,
                    Email_Address=None, Date_of_Birth=None, **extra_fields):
        if not Email_Address:
            raise ValueError('Users must have an email address')
        email_check = User.objects.filter(email=Email_Address)
        if email_check.exists():
            raise ValueError('This Email already exists')
        if len(password) < 5: #todo: more secure password
            raise forms.ValidationError('Your password should have more than 5 characters')
        user = self.model(
            Email_Address=self.normalize_email(Email_Address),
            #name=self.normalize_email(email),
            Date_of_Birth=birthday,
            zipcode=zipcode,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, Email_Address, password):
        user = self.create_user(
            Email_Address=self.normalize_email(Email_Address),
            password=password,
            is_superuser=True,
        )
        user.is_admin = True
        user.is_active=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
    editable=False)
    Email_Address = models.EmailField(verbose_name="email", max_length=60, unique=True, blank=True, null=True, default=None)
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=30, blank=True, null=True, default=random.randint(1000, 9999))
    Date_of_Birth = models.CharField(max_length=30, blank=True, null=True,
     default=None)
    username = models.CharField(max_length=30,unique=True, blank=True, null=True)
    bio = models.TextField(max_length=70, blank=True, null=True)
    #adresse
    country = models.CharField(max_length=30, blank=True, null=True)
    zipcode = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    street = models.CharField(max_length=30, blank=True, null=True)
    house_number = models.IntegerField(blank=True, null=True)

    longitude = models.FloatField(max_length=17,blank=True, null=True)
    latitude = models.FloatField(max_length=17,blank=True, null=True)

    profile_picture = models.ImageField(upload_to='', max_length=800)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_freezed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'Email_Address'

    objects = MyAccountManager()

    class Meta:
        db_table = "tbl_users"

    def __str__(self):
        return str(self.Email_Address)


    def has_perm(self, perm, obj=None): return self.is_superuser

    def has_module_perms(self, app_label): return self.is_superuser