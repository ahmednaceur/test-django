
# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

from rest_framework_simplejwt.tokens import RefreshToken
from random import choices
from string import ascii_letters
from django.conf import settings
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


AUTH_PROVIDERS = {  'email': 'email'}


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class LinkManger(BaseUserManager):
    def create_Link(self, original_link, shortened_link, clicks ,email_user):
        if not email_user:
            raise ValueError('message must have email address')
        link = self.model(email_user=email_user)
        link.original_link = original_link
        link.shortened_link = shortened_link
        link.clicks = clicks

        link.save(using=self._db)
        return link

class Link(models.Model):
    email_user = models.CharField(max_length=250)
    original_link = models.URLField()
    shortened_link = models.URLField(blank=True, null=True)
    clicks = models.IntegerField(default=0)
    Objects = LinkManger()
    def shortener(self):
        while True:
            random_string = ''.join(choices(ascii_letters, k=6))
            new_link = settings.HOST_URL + '/' + random_string

            if not Link.Objects.filter(shortened_link=new_link).exists():
                break

        return new_link

    def save(self, *args, **kwargs):
        if not self.shortened_link:
            new_link = self.shortener()
            self.shortened_link = new_link
        return super().save(*args, **kwargs)

