from core.permissions import IsSeniorOrAdmin, ReadOnlyForJunior
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Asset
from .serializers import AssetSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForJunior]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), ReadOnlyForJunior(), IsSeniorOrAdmin()]

        return [IsAuthenticated(), ReadOnlyForJunior()]
