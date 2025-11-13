from apps.portifolios.models import Portfolio
from core.permissions import IsSeniorOrAdmin, ReadOnlyForJunior
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .serializers import TransactionCreateSerializer


class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        ReadOnlyForJunior,
        IsSeniorOrAdmin,
    ]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        portfolio_pk = self.kwargs.get("portfolio_pk") or self.kwargs.get("pk")
        portfolio = None
        if portfolio_pk:
            user = getattr(self.request, "user", None)
            profile = getattr(user, "profile", None)
            qs = Portfolio.objects.all()
            if profile is None:
                scoped_qs = qs.none()
            elif profile.role == profile.ROLE_ADMIN_SUPER:
                scoped_qs = qs
            else:
                scoped_qs = qs.filter(host=profile.host)

            portfolio = get_object_or_404(scoped_qs, pk=portfolio_pk)
            self.check_object_permissions(self.request, portfolio)
        if portfolio is not None:
            ctx["portfolio"] = portfolio
        return ctx

    def perform_create(self, serializer):
        serializer.save()
