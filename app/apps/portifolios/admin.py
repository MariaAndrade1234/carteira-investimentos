from django.contrib import admin

from .models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("nome", "host", "criado_por", "criado_em")

    search_fields = ("nome", "host")
