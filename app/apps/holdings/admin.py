from django.contrib import admin

from .models import Holding


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset", "quantidade_total", "preco_medio")

    list_select_related = ("portfolio", "asset")
