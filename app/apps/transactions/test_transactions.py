import pytest
from apps.accounts.models import UserProfile
from apps.assets.models import Asset
from apps.holdings.models import Holding
from apps.portifolios.models import Portfolio
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_venda_excede_quantidade_retorna_400():
    user = User.objects.create_user(username="senior", password="pass")
    profile = UserProfile.objects.get(user=user)
    profile.role = UserProfile.ROLE_INVESTIDOR_SENIOR
    profile.host = "alpha"
    profile.save()

    portfolio = Portfolio.objects.create(nome="P1", host="alpha", criado_por=user)
    asset = Asset.objects.create(ticker="ABC", nome="Asset ABC", tipo="ACAO")
    _ = Holding.objects.create(
        portfolio=portfolio, asset=asset, quantidade_total=10, preco_medio=5
    )

    client = APIClient()
    client.login(username="senior", password="pass")

    url = f"/api/portfolios/{portfolio.id}/transactions/"
    payload = {
        "asset": asset.id,
        "tipo": "VENDA",
        "quantidade": "20.00",
        "preco": "10.00",
        "data": "2025-11-11",
    }

    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert "Venda" in str(resp.data) or "quantidade" in str(resp.data)


@pytest.mark.django_db
def test_senior_nao_pode_criar_transacao_em_portfolio_de_outro_host():
    user = User.objects.create_user(username="senior_other", password="pass")
    profile = UserProfile.objects.get(user=user)
    profile.role = UserProfile.ROLE_INVESTIDOR_SENIOR
    profile.host = "alpha"
    profile.save()

    other_user = User.objects.create_user(username="owner_beta", password="pass")
    portfolio_beta = Portfolio.objects.create(
        nome="P_beta", host="beta", criado_por=other_user
    )
    asset = Asset.objects.create(ticker="ZZZ", nome="Asset Z", tipo="ACAO")

    client = APIClient()
    client.login(username="senior_other", password="pass")

    url = f"/api/portfolios/{portfolio_beta.id}/transactions/"
    payload = {
        "asset": asset.id,
        "tipo": "COMPRA",
        "quantidade": "1.00",
        "preco": "10.00",
        "data": "2025-11-11",
    }

    resp = client.post(url, payload, format="json")
    assert resp.status_code in (403, 404)
