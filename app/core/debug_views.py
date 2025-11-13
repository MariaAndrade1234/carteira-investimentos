from decimal import Decimal
import json
from datetime import date

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.portifolios.models import Portfolio
from apps.assets.models import Asset
from apps.transactions.models import Transaction
from apps.holdings.models import Holding


@csrf_exempt
def test_atomic_view(request):
    """Endpoint de teste (apenas para DEBUG/testes) que verifica atomicidade.

    Recebe um JSON com: portfolio (uuid), asset (id), tipo, quantidade, preco.
    A view cria uma Transaction e então lança uma exceção para forçar rollback.
    Quando `ATOMIC_REQUESTS = True`, as alterações no banco devem ser revertidas.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Apenas POST"}, status=405)

    payload = json.loads(request.body or b"{}")
    portfolio = Portfolio.objects.get(pk=payload["portfolio"])  # pode lançar
    asset = Asset.objects.get(pk=payload["asset"])  # pode lançar
    quantidade = Decimal(str(payload.get("quantidade", "0")))
    preco = Decimal(str(payload.get("preco", "0")))

    holding, _ = Holding.objects.get_or_create(portfolio=portfolio, asset=asset)

    Transaction.objects.create(
        holding=holding,
        tipo=payload.get("tipo", "COMPRA"),
        quantidade=quantidade,
        preco=preco,
        data=date.today(),
        criado_por=request.user,
    )

    # Lança erro proposital após operações no BD para testar rollback
    raise RuntimeError("forçar rollback para teste de atomicidade")
