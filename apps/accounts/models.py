from __future__ import annotations

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .utils import PlayerCodeGenerator


class PlayerManager(BaseUserManager):
    def create_user(self, email: str, name: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError('Players must provide an email address')
        email = self.normalize_email(email)
        player = self.model(email=email, name=name, **extra_fields)
        player.set_password(password or self.make_random_password())
        player.save(using=self._db)
        return player

    def create_superuser(self, email: str, name: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is False:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email=email, name=name, password=password, **extra_fields)


class Player(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120)
    unique_code = models.CharField(max_length=12, unique=True, editable=False)
    organization = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = PlayerManager()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = PlayerCodeGenerator.generate()
        if not self.last_login:
            self.last_login = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.unique_code})"
