import uuid

from django.contrib.auth.models import User
from django.db import models


class Portfolio(models.Model):
    id: models.UUIDField = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    nome: models.CharField = models.CharField(max_length=100)
    host: models.CharField = models.CharField(max_length=50)  # multi-tenant
    criado_por: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    criado_em: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    atualizado_em: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.host})"

    class Meta:
        ordering = ["id"]
