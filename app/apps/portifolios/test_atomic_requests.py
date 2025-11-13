import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import override_settings

from apps.assets.models import Asset
from apps.holdings.models import Holding
from apps.portifolios.models import Portfolio


@pytest.mark.django_db
def test_atomic_requests_rolls_back_on_error():
    # setup: create senior user, portfolio, asset, holding
    user = User.objects.create_user(username="senior_test", password="pass")
    user.save()
    # ensure profile exists and is senior
    profile = user.profile
    profile.role = user.profile.ROLE_INVESTIDOR_SENIOR
    profile.host = "alpha"
    profile.save()

    portfolio = Portfolio.objects.create(nome="P1", host="alpha", criado_por=user)
    asset = Asset.objects.create(ticker="DEMOX", nome="Demo X", tipo="ACAO")

    # ensure initial holding
    holding, _ = Holding.objects.get_or_create(portfolio=portfolio, asset=asset)
    holding.quantidade_total = Decimal("10.00")
    holding.preco_medio = Decimal("5.00")
    holding.save()

    payload = {
        "portfolio": str(portfolio.id),
        "asset": asset.id,
        "tipo": "COMPRA",
        "quantidade": "5.00",
        "preco": "10.00",
    }

    # Use a temporary URLConf so the request goes through middleware (ATOMIC_REQUESTS).
    # The view raises a RuntimeError; the test asserts that the exception is
    # raised and then verifies the DB was rolled back.
    with override_settings(ROOT_URLCONF="tests.fixtures.urls_for_tests"):
        client = APIClient()
        client.login(username="senior_test", password="pass")

        with pytest.raises(RuntimeError):
            client.post("/api/test_atomic/", payload, format="json")

    # holding should remain unchanged because the request should be atomic
    refreshed = Holding.objects.get(pk=holding.pk)
    assert float(refreshed.quantidade_total) == float(Decimal("10.00"))
