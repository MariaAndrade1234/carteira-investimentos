import pytest
from apps.accounts.models import UserProfile
from apps.portifolios.models import Portfolio
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_user_cannot_access_portfolio_of_other_host():
    user = User.objects.create_user(username="user_alpha", password="pass")

    profile = UserProfile.objects.get(user=user)
    profile.host = "alpha"
    profile.role = UserProfile.ROLE_INVESTIDOR_JUNIOR
    profile.save()

    admin = User.objects.create_user(username="admin_beta", password="pass")

    portfolio = Portfolio.objects.create(nome="P_beta", host="beta", criado_por=admin)

    client = APIClient()
    client.login(username="user_alpha", password="pass")

    url = f"/api/portfolios/{portfolio.id}/"
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_investidor_junior_cannot_create_portfolio():
    user = User.objects.create_user(username="junior", password="pass")

    profile = UserProfile.objects.get(user=user)
    profile.host = "alpha"
    profile.role = UserProfile.ROLE_INVESTIDOR_JUNIOR
    profile.save()

    client = APIClient()
    client.login(username="junior", password="pass")

    url = "/api/portfolios/"
    payload = {"nome": "Novo", "host": "alpha"}
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 403
