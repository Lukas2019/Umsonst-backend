from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth import get_user_model
import uuid

Users = get_user_model()

class MyAccountManager(BaseUserManager):
    def create_user(self, email, fullname=None, birthday=None, zipcode=None,password=None
                    ):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            Email_Address=self.normalize_email(email),
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
        )
        user.is_admin = True
        user.is_active=True
        user.save(using=self._db)

class Users(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
    editable=False)
    Email_Address = models.EmailField(verbose_name="email", max_length=60, unique=True, blank=True, null=True, default=None)
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

    USERNAME_FIELD = 'Email_Address'

    objects = MyAccountManager()

    class Meta:
        db_table = "tbl_users"

    def __str__(self):
        return str(self.email)


    def has_perm(self, perm, obj=None): return self.is_superuser

    def has_module_perms(self, app_label): return self.is_superuser