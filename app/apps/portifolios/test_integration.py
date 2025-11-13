from decimal import Decimal

import pytest
from apps.accounts.models import UserProfile
from apps.assets.models import Asset
from apps.holdings.models import Holding
from apps.portifolios.models import Portfolio
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_senior_can_create_portfolio_same_host():
    user = User.objects.create_user(username="senior_create", password="pass")
    profile = UserProfile.objects.get(user=user)
    profile.role = UserProfile.ROLE_INVESTIDOR_SENIOR
    profile.host = "alpha"
    profile.save()

    client = APIClient()
    client.login(username="senior_create", password="pass")

    url = "/api/portfolios/"
    payload = {"nome": "Portfolio Senior", "host": "ignored-host"}
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201
    data = resp.json()
    # host should be set to user's host regardless of provided value
    assert data.get("host") == "alpha"
    assert data.get("nome") == "Portfolio Senior"


@pytest.mark.django_db
def test_compra_adjusts_holding():
    user = User.objects.create_user(username="senior_trade", password="pass")
    profile = UserProfile.objects.get(user=user)
    profile.role = UserProfile.ROLE_INVESTIDOR_SENIOR
    profile.host = "alpha"
    profile.save()

    portfolio = Portfolio.objects.create(nome="Ptrade", host="alpha", criado_por=user)
    asset = Asset.objects.create(ticker="XYZ", nome="Asset XYZ", tipo="ACAO")
    # initial holding
    holding = Holding.objects.create(
        portfolio=portfolio,
        asset=asset,
        quantidade_total=Decimal("2.00"),
        preco_medio=Decimal("8.00"),
    )

    client = APIClient()
    client.login(username="senior_trade", password="pass")

    url = f"/api/portfolios/{portfolio.id}/transactions/"
    payload = {
        "asset": asset.id,
        "tipo": "COMPRA",
        "quantidade": "5.00",
        "preco": "10.00",
        "data": "2025-11-11",
    }
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201

    holding.refresh_from_db()
    # expected: novo_total = 7, novo_preco_medio = 66/7 ~= 9.428571
    assert float(holding.quantidade_total) == pytest.approx(7.0, rel=1e-6)
    # model stores preco_medio with 2 decimal places, so compare rounded value
    assert float(holding.preco_medio) == pytest.approx(round(66.0 / 7.0, 2), rel=1e-6)


@pytest.mark.django_db
def test_list_paginado_filtrado_por_host():
    admin = User.objects.create_user(username="admin", password="pass")
    # create two portfolios different hosts
    Portfolio.objects.create(nome="P_alpha", host="alpha", criado_por=admin)
    Portfolio.objects.create(nome="P_beta", host="beta", criado_por=admin)

    user = User.objects.create_user(username="viewer", password="pass")
    profile = UserProfile.objects.get(user=user)
    profile.role = UserProfile.ROLE_INVESTIDOR_JUNIOR
    profile.host = "alpha"
    profile.save()

    client = APIClient()
    client.login(username="viewer", password="pass")

    url = "/api/portfolios/"
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    # paginated response with 'results'
    assert "results" in data
    results = data["results"]
    assert len(results) == 1
    assert results[0]["host"] == "alpha"


@pytest.mark.django_db
def test_assets_and_holdings_list_endpoints():
    user = User.objects.create_user(username="u", password="pass")
    profile = UserProfile.objects.get(user=user)
    profile.role = UserProfile.ROLE_INVESTIDOR_JUNIOR
    profile.host = "alpha"
    profile.save()

    # create assets and holdings
    a1 = Asset.objects.create(ticker="A1", nome="A1", tipo="ACAO")
    Asset.objects.create(ticker="A2", nome="A2", tipo="FII")
    portfolio = Portfolio.objects.create(nome="P", host="alpha", criado_por=user)
    Holding.objects.create(
        portfolio=portfolio, asset=a1, quantidade_total=1, preco_medio=10
    )

    client = APIClient()
    client.login(username="u", password="pass")

    resp_assets = client.get("/api/assets/")
    assert resp_assets.status_code == 200
    assets_data = resp_assets.json()
    assert "results" in assets_data
    assert any(item["ticker"] == "A1" for item in assets_data["results"])

    resp_holdings = client.get("/api/holdings/")
    assert resp_holdings.status_code == 200
    holdings_data = resp_holdings.json()
    assert "results" in holdings_data
    assert len(holdings_data["results"]) >= 1
