from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_CHOICES = [
    ('superadmin', 'Super Admin'),
    ('store_officer', 'Store Officer'),
    ('hod', 'Head of Department'),
    ('auditor', 'Auditor'),
    ('bursar', 'Bursar'),
]


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='store_officer')
    department = models.ForeignKey(
        'core.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )
    phone = models.CharField(max_length=20, blank=True)
    staff_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    must_change_password = models.BooleanField(default=True)

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_role_display_badge(self):
        colours = {
            'superadmin': 'danger',
            'store_officer': 'info',
            'hod': 'warning',
            'auditor': 'success',
            'bursar': 'neutral',
        }
        return colours.get(self.role, 'neutral')
