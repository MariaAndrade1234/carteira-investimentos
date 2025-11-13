from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_INVESTIDOR_JUNIOR = "INVESTIDOR_JUNIOR"
    ROLE_INVESTIDOR_SENIOR = "INVESTIDOR_SENIOR"
    ROLE_ADMIN_SUPER = "ADMIN_SUPER"

    ROLE_CHOICES = (
        (ROLE_INVESTIDOR_JUNIOR, "Investidor Júnior"),
        (ROLE_INVESTIDOR_SENIOR, "Investidor Sênior"),
        (ROLE_ADMIN_SUPER, "Admin Super"),
    )

    user: models.OneToOneField = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )

    role: models.CharField = models.CharField(
        max_length=30, choices=ROLE_CHOICES, default=ROLE_INVESTIDOR_JUNIOR
    )

    host: models.CharField = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
