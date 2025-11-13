from apps.assets.models import Asset
from apps.portifolios.models import Portfolio
from django.db import models
from typing import cast


class Holding(models.Model):
    portfolio: models.ForeignKey = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="holdings"
    )
    asset: models.ForeignKey = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantidade_total: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    preco_medio: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    def __str__(self):
        # cast to help the type checker know these are model instances
        asset = cast(Asset, self.asset)
        portfolio = cast(Portfolio, self.portfolio)
        return f"{asset.ticker} - {portfolio.nome}"

    class Meta:
        ordering = ["id"]
