from django.db import models
from django.contrib.auth.models import User
from typing import cast

from apps.holdings.models import Holding

TIPO_TRANSACAO = (
    ("COMPRA", "Compra"),
    ("VENDA", "Venda"),
)


class Transaction(models.Model):
    # Campos do modelo definidos em múltiplas linhas para manter largura < 88
    holding = models.ForeignKey(
        Holding,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_TRANSACAO,
    )

    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    preco = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.atualizar_holding()

    def atualizar_holding(self):
        # cast para ajudar o verificador de tipos; o Django atribui instâncias
        # de modelo dinamicamente nos campos ForeignKey.
        holding = cast(Holding, self.holding)
        if self.tipo == "COMPRA":
            novo_total = holding.quantidade_total + self.quantidade
            novo_preco_medio = (
                (holding.quantidade_total * holding.preco_medio)
                + (self.quantidade * self.preco)
            ) / novo_total
            holding.quantidade_total = novo_total
            holding.preco_medio = novo_preco_medio
        elif self.tipo == "VENDA":
            holding.quantidade_total -= self.quantidade
        holding.save()

    class Meta:
        ordering = ["id"]
