from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth import get_user_model
import uuid
from django import forms
import random
# Mail
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.conf import settings
#Users = get_user_model()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    url = reverse('user:password_reset_change', kwargs={'token': reset_password_token.key})


    # the below like concatinates your websites reset password url and the reset email token which will be required at a later stage
    email_plaintext_message = "Open the link to reset your password " + settings.HOSTNAME + url # "{}{}".format(instance.request.build_absolute_uri(url), reset_password_token.key)
    
    """
        this below line is the django default sending email function, 
        takes up some parameter (title(email title), message(email body), from(email sender), to(recipient(s))
    """
    send_mail(
        # title:
        "Password Reset for {title}".format(title="Crediation portal account"),
        # message:
        email_plaintext_message,
        # from:https://stackoverflow.com/questions/10384657/django-send-mail-not-working-no-email-delivered
        "Umsonst@klimacamp-siegen.de",
        # to:
        recipient_list = [reset_password_token.user.email],
        fail_silently=False,
    )


class MyAccountManager(BaseUserManager):
    def create_user(self, fullname=None, birthday=None, zipcode=None,password=None,
                    email=None, Date_of_Birth=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email_check = User.objects.filter(email=email)
        if email_check.exists():
            raise ValueError('This Email already exists')
        if len(password) < 5: #todo: more secure password
            raise forms.ValidationError('Your password should have more than 5 characters')
        user = self.model(
            email=self.normalize_email(email),
            #name=self.normalize_email(email),
            Date_of_Birth=birthday,
            zipcode=zipcode,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            is_superuser=True,
        )
        user.is_admin = True
        user.is_active=True
        user.is_staff=True
        user.is_superuser=True
        user.save() #using=self._db)

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
    editable=False)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, blank=True, null=True, default=None)
    #email_verified = models.BooleanField(default=False)
    #verification_code = models.CharField(max_length=30, blank=True, null=True, default=random.randint(1000, 9999))
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

    profile_picture = models.ImageField(upload_to='', max_length=800, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_freezed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = MyAccountManager()

    class Meta:
        db_table = "tbl_users"

    def __str__(self):
        return str(self.email)


    def has_perm(self, perm, obj=None): return self.is_superuser

    def has_module_perms(self, app_label): return self.is_superuser