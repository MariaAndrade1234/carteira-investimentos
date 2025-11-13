from core.permissions import ReadOnlyForJunior
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Holding
from .serializers import HoldingSerializer


class HoldingViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for holdings, scoped by host/role.

    This viewset scopes holdings based on the related portfolio host. Admin
    users see all holdings; other users see only holdings for their
    profile.host.
    """

    serializer_class = HoldingSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForJunior]

    def get_queryset(self):
        qs = Holding.objects.select_related("asset", "portfolio").all()
        user = getattr(self.request, "user", None)
        profile = getattr(user, "profile", None)
        if profile is None:
            return qs.none()
        if profile.role == profile.ROLE_ADMIN_SUPER:
            return qs
        return qs.filter(portfolio__host=profile.host)
