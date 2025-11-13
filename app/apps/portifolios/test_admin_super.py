import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
from apps.portifolios.models import Portfolio


@pytest.mark.django_db
def test_admin_super_can_list_and_create_across_hosts():
    # criar admin super
    admin = User.objects.create_user(username="admin_super_test", password="pass")
    profile = UserProfile.objects.get(user=admin)
    profile.role = UserProfile.ROLE_ADMIN_SUPER
    profile.host = ""  # global
    profile.save()

    # criar portfolios em hosts distintos
    Portfolio.objects.create(nome="P_alpha_admin", host="alpha", criado_por=admin)
    Portfolio.objects.create(nome="P_beta_admin", host="beta", criado_por=admin)

    client = APIClient()
    client.login(username="admin_super_test", password="pass")

    # admin deve listar portfólios de todos os hosts
    resp = client.get("/api/portfolios/")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    hosts = {item.get("host") for item in data.get("results", [])}
    assert "alpha" in hosts and "beta" in hosts

    # admin pode criar portfolio para outro host explicitamente
    payload = {"nome": "Admin Created", "host": "beta"}
    resp2 = client.post("/api/portfolios/", payload, format="json")
    assert resp2.status_code == 201
    created = resp2.json()
    # host informado deve ser respeitado para ADMIN_SUPER
    assert created.get("host") == "beta"
