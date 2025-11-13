from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from apps.portifolios.views import PortfolioViewSet
from apps.transactions.views import TransactionCreateView
from apps.assets.views import AssetViewSet
from apps.holdings.views import HoldingViewSet


router = routers.DefaultRouter()
router.register(r"portfolios", PortfolioViewSet, basename="portfolios")
router.register(r"assets", AssetViewSet, basename="assets")
router.register(r"holdings", HoldingViewSet, basename="holdings")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api/portfolios/<uuid:pk>/transactions/",
        TransactionCreateView.as_view(),
        name="portfolio-transactions",
    ),
]

# Nota: o endpoint de teste `test_atomic_view` é usado apenas pelos testes.
# Não o registramos por padrão aqui para evitar exposição acidental em
# ambientes de desenvolvimento/produção. Os testes registram a URL
# temporariamente via um URLConf em `tests/fixtures/urls_for_tests.py`.
