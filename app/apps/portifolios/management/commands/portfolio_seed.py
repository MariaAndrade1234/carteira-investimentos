from decimal import Decimal

from apps.accounts.models import UserProfile
from apps.assets.models import Asset
from apps.holdings.models import Holding
from apps.portifolios.models import Portfolio
from apps.transactions.models import Transaction
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Popular dados de demonstração para portfolios (multi-tenant)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Mostrar o que seria criado sem salvar",
        )
        parser.add_argument(
            "--hosts",
            nargs="*",
            default=["alpha", "beta"],
            help="Hosts a criar (padrão: alpha beta)",
        )
        parser.add_argument(
            "--num-assets", type=int, default=3, help="Número de ativos de demonstração"
        )
        parser.add_argument(
            "--holdings-per-portfolio",
            type=int,
            default=1,
            help="Quantidade de holdings por portfolio",
        )
        parser.add_argument(
            "--transactions-per-portfolio",
            type=int,
            default=1,
            help="Quantidade de transações por portfolio",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        hosts = options.get("hosts") or ["alpha", "beta"]

        actions: list[str] = []

        admin_username = "admin_super"
        admin_user = User.objects.filter(username=admin_username).first()
        if not admin_user:
            actions.append(f"create User(username='{admin_username}')")
        else:
            actions.append(f"user exists: {admin_username}")

        # options.get() pode retornar None; coerce para int
        num_assets = int(options.get("num_assets") or 3)

        assets_to_create: list[dict] = []
        for i in range(1, num_assets + 1):
            assets_to_create.append(
                {
                    "ticker": f"DEMO{i}",
                    "nome": f"Demo Asset {i}",
                    "tipo": "ACAO" if i % 2 == 1 else "FII",
                }
            )
        for asset_spec in assets_to_create:
            if not Asset.objects.filter(ticker=asset_spec["ticker"]).exists():
                actions.append(f"create Asset(ticker='{asset_spec['ticker']}')")
            else:
                actions.append(f"asset exists: {asset_spec['ticker']}")

        holdings_per = int(options.get("holdings_per_portfolio") or 1)
        txs_per = int(options.get("transactions_per_portfolio") or 1)

        for host in hosts:
            senior = f"senior_{host}"
            junior = f"junior_{host}"

            if not User.objects.filter(username=senior).exists():
                actions.append(
                    (
                        f"create User(username='{senior}') and set profile "
                        f"host={host} role=INVESTIDOR_SENIOR"
                    )
                )
            else:
                actions.append(f"user exists: {senior}")

            if not User.objects.filter(username=junior).exists():
                actions.append(
                    (
                        f"create User(username='{junior}') and set profile "
                        f"host={host} role=INVESTIDOR_JUNIOR"
                    )
                )
            else:
                actions.append(f"user exists: {junior}")

            pname = f"Demo {host} Portfolio"
            if not Portfolio.objects.filter(nome=pname, host=host).exists():
                actions.append(f"create Portfolio(nome='{pname}', host='{host}')")
            else:
                actions.append(f"portfolio exists: {pname} ({host})")

        if dry_run:
            self.stdout.write("DRY RUN - as seguintes ações seriam executadas:")
            for a in actions:
                self.stdout.write(" - " + a)
            return

        admin_user, created = User.objects.get_or_create(
            username=admin_username, defaults={"password": "admin"}
        )
        if created:
            admin_user.set_password("admin")
            admin_user.save()
        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = UserProfile.ROLE_ADMIN_SUPER
        admin_profile.host = ""
        admin_profile.save()

        for asset_spec in assets_to_create:
            Asset.objects.get_or_create(
                ticker=asset_spec["ticker"],
                defaults={"nome": asset_spec["nome"], "tipo": asset_spec["tipo"]},
            )

        for host in hosts:
            senior_username = f"senior_{host}"
            junior_username = f"junior_{host}"
            senior_user, created = User.objects.get_or_create(username=senior_username)
            if created:
                senior_user.set_password("pass")
                senior_user.save()
            senior_profile, _ = UserProfile.objects.get_or_create(user=senior_user)
            senior_profile.role = UserProfile.ROLE_INVESTIDOR_SENIOR
            senior_profile.host = host
            senior_profile.save()

            junior_user, created = User.objects.get_or_create(username=junior_username)
            if created:
                junior_user.set_password("pass")
                junior_user.save()
            junior_profile, _ = UserProfile.objects.get_or_create(user=junior_user)
            junior_profile.role = UserProfile.ROLE_INVESTIDOR_JUNIOR
            junior_profile.host = host
            junior_profile.save()

            pname = f"Demo {host} Portfolio"
            portfolio, _ = Portfolio.objects.get_or_create(
                nome=pname, host=host, defaults={"criado_por": senior_user}
            )

            assets = list(Asset.objects.all())
            for idx in range(holdings_per):
                asset = assets[idx % len(assets)] if assets else None
                if asset:
                    holding, _ = Holding.objects.get_or_create(
                        portfolio=portfolio,
                        asset=asset,
                        defaults={
                            "quantidade_total": Decimal("100.00"),
                            "preco_medio": Decimal("10.00"),
                        },
                    )
                    for _t in range(txs_per):
                        Transaction.objects.create(
                            holding=holding,
                            tipo="COMPRA",
                            quantidade=Decimal("100.00"),
                            preco=Decimal("10.00"),
                            data=timezone.now().date(),
                            criado_por=senior_user,
                        )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
        admin_profile.role = UserProfile.ROLE_ADMIN_SUPER
