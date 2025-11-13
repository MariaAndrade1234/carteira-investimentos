from core.permissions import (
    HostAndRoleBasedScopeMixin,
    IsSeniorOrAdmin,
    ReadOnlyForJunior,
)
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Portfolio
from .serializers import PortfolioSerializer


class PortfolioViewSet(HostAndRoleBasedScopeMixin, viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForJunior]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), ReadOnlyForJunior(), IsSeniorOrAdmin()]

        return [IsAuthenticated(), ReadOnlyForJunior()]

    def perform_create(self, serializer):
        profile = getattr(self.request.user, "profile", None)
        if profile and profile.role == profile.ROLE_INVESTIDOR_SENIOR:
            serializer.save(criado_por=self.request.user, host=profile.host)
            return
        serializer.save(criado_por=self.request.user)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        portfolio = get_object_or_404(self.get_queryset(), pk=pk)
        holdings = portfolio.holdings.all()
        data = []
        for h in holdings:
            data.append(
                {
                    "asset": h.asset.ticker,
                    "quantidade": float(h.quantidade_total),
                    "preco_medio": float(h.preco_medio),
                    "valor_total": float(h.preco_medio * h.quantidade_total),
                }
            )
        return Response(data)
