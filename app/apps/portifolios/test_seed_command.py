from io import StringIO

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_portfolio_seed_dry_run_parametrized():
    out = StringIO()
    call_command(
        "portfolio_seed",
        "--dry-run",
        "--hosts",
        "alpha",
        "--num-assets",
        "2",
        "--holdings-per-portfolio",
        "2",
        "--transactions-per-portfolio",
        "1",
        stdout=out,
    )
    output = out.getvalue()
    assert "create Asset(ticker='DEMO1')" in output
    assert "create Asset(ticker='DEMO2')" in output
    assert "create User(username='senior_alpha')" in output
    assert "create User(username='junior_alpha')" in output
    assert "create Portfolio(nome='Demo alpha Portfolio'" in output
