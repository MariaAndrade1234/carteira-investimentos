from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "holding",
        "tipo",
        "quantidade",
        "preco",
        "criado_por",
        "data",
    )

    list_select_related = ("holding", "criado_por")
