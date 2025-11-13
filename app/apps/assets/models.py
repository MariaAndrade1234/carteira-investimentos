from django.db import models

TIPO_CHOICES = (
    ("ACAO", "Ação"),
    ("FII", "Fundo Imobiliário"),
    ("RENDA_FIXA", "Renda Fixa"),
)


class Asset(models.Model):
    ticker: models.CharField = models.CharField(max_length=10, unique=True)
    nome: models.CharField = models.CharField(max_length=100)
    tipo: models.CharField = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.ticker} - {self.nome}"

    class Meta:
        ordering = ["id"]
