from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ('student', 'Student/User'),
        ('faculty', 'Faculty/Staff'),
        ('maintenance', 'Maintenance/Support'),
        ('admin', 'Administrator'),
    ]

    SPECIALIZATION_CHOICES = [
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('cleaning', 'Cleaning'),
        ('it', 'Wi-Fi/IT'),
        ('equipment', 'Classroom Equipment'),
        ('security', 'Security'),
        ('other', 'Other'),
    ]

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    specialization = models.CharField(
        max_length=20,
        choices=SPECIALIZATION_CHOICES,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username