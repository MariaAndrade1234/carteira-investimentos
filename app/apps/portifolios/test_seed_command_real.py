import pytest
from apps.accounts.models import UserProfile
from apps.assets.models import Asset
from apps.holdings.models import Holding
from apps.portifolios.models import Portfolio
from apps.transactions.models import Transaction
from django.contrib.auth.models import User
from django.core.management import call_command


@pytest.mark.django_db
def test_portfolio_seed_creates_data():
    call_command(
        "portfolio_seed",
        "--hosts",
        "alpha",
        "--num-assets",
        "2",
        "--holdings-per-portfolio",
        "1",
        "--transactions-per-portfolio",
        "1",
    )

    assert User.objects.filter(username="admin_super").exists()
    admin = User.objects.get(username="admin_super")
    admin_profile = UserProfile.objects.get(user=admin)
    assert admin_profile.role == UserProfile.ROLE_ADMIN_SUPER

    assert Asset.objects.filter(ticker="DEMO1").exists()
    assert Asset.objects.filter(ticker="DEMO2").exists()

    assert User.objects.filter(username="senior_alpha").exists()
    assert User.objects.filter(username="junior_alpha").exists()

    assert Portfolio.objects.filter(nome="Demo alpha Portfolio", host="alpha").exists()

    assert Holding.objects.filter(portfolio__host="alpha").exists()
    assert Transaction.objects.filter(holding__portfolio__host="alpha").exists()
