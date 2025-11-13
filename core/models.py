from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER = 'USER'
    SELLER = 'SELLER'
    ADMIN = 'ADMIN'
    ROLE_CHOICES = [
        (USER, 'User'),
        (SELLER, 'Seller'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.role})"




class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    is_super_admin = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin: {self.user.username}"



