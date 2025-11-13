
# Carteira de Investimentos

API para gestão de carteiras, ativos, posições e transações. Projeto construído com
Django e Django REST Framework, com suporte mínimo a multitenancy por `host` e RBAC
(perfis: INVESTIDOR_JUNIOR, INVESTIDOR_SENIOR, ADMIN_SUPER).

## Visão geral

Este repositório contém uma API que permite gerenciar portfólios (por host), ativos,
posições (holdings) e transações. Há regras básicas de negócio e permissões para
controlar quem pode criar/atualizar recursos (ex.: somente INVESTIDOR_SENIOR do mesmo
`host` ou ADMIN_SUPER podem modificar certas entidades).

Principais componentes

- Django + Django REST Framework
- Modelos: `Portfolio`, `Asset`, `Holding`, `Transaction`, `UserProfile`
- Permissões e mixins para scoping por `host`
- Comando management `portfolio_seed` para popular dados de demonstração
- Testes com `pytest` e checagem de tipos com `mypy`

## Requisitos

- Python 3.11+
- Um virtualenv (recomendado)
- Dependências listadas em `requirements.txt`

## Setup local (Windows / PowerShell)

1) Criar e ativar o virtualenv

```powershell
python -m venv venv
; .\venv\Scripts\Activate.ps1
```

2) Instalar dependências

```powershell
pip install -r requirements.txt
```

3) Migrar o banco de dados

Observação: muitas instruções abaixo assumem que você está na raiz do repositório
(`carteira-investimentos`). O Django project está na pasta `app/`.

```powershell
# ativar o venv se ainda não estiver ativo
.\venv\Scripts\Activate.ps1
# criar migrations e aplicar
Set-Location .\app
python manage.py makemigrations
python manage.py migrate
```

## Arquivo `.env` e `SECRET_KEY`

Este projeto aceita um arquivo `.env` colocado na raiz do repositório (ex.:
`/caminho/para/carteira-investimentos/.env`). As variáveis definidas ali são
carregadas automaticamente em desenvolvimento quando `python-dotenv` está
instalado.

Exemplo mínimo de `.env.example` (não adicione `.env` ao repositório):

```text
# .env.example
DEBUG=True
SECRET_KEY=replace_with_a_secure_value
```

Como gerar uma `SECRET_KEY` segura (com o venv ativado):

```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie o valor gerado e cole em `.env` como o valor de `SECRET_KEY`.

Recomendações:
- Adicione `.env` ao `.gitignore` para não versionar segredos.
- Em produção, configure `SECRET_KEY` como variável de ambiente no ambiente
  de execução (ex.: secrets do provedor de nuvem, GitHub Secrets + deploy pipeline).

## Executando a aplicação

Rodar o servidor de desenvolvimento (a partir da pasta `app/` com venv ativado):

```powershell
Set-Location .\app
python manage.py runserver
```

A API ficará disponível por padrão em `http://127.0.0.1:8000/`.

## Dados de demonstração (seed)

Visualizar as ações que seriam executadas (dry-run):

```powershell
Set-Location .\app
python manage.py portfolio_seed --dry-run
```

Criar os dados de demonstração (atenção: irá alterar o banco de dados):

```powershell
Set-Location .\app
python manage.py portfolio_seed
```

## Testes

Instruções claras para rodar os testes localmente.

1) Ative o venv e entre na pasta `app/`:

```powershell
.\venv\Scripts\Activate.ps1
Set-Location .\app
```

2) (Opcional) defina a variável de ambiente do Django explicitamente:

```powershell
$env:DJANGO_SETTINGS_MODULE='core.settings'
```

3) Rodar todos os testes com `pytest`:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

4) Rodar um teste específico — exemplo: teste de atomicidade (rollback):

```powershell
.\venv\Scripts\python.exe -m pytest apps/portifolios/test_atomic_requests.py::test_atomic_requests_rolls_back_on_error -q
```

Notas sobre o teste de atomicidade:
- O teste utiliza uma view de debug (`core.debug_views.test_atomic_view`) que
  cria uma `Transaction` e em seguida lança uma exceção para forçar rollback.
- A view de teste não é registrada em URLs de produção — os testes usam um
  URLConf temporário/isolado.

## Tipagem e linters

- Executar checagem de tipos (mypy):

```powershell
.\venv\Scripts\python.exe -m mypy app --show-error-codes
```

- Rodar flake8 (configurado para max-line-length=88):

```powershell
.\venv\Scripts\python.exe -m flake8 --max-line-length=88
```

## Estrutura do projeto (resumo)

```
app/
├─ core/                # settings, urls, wsgi
├─ apps/
│  ├─ assets/
│  ├─ holdings/
│  ├─ portifolios/
│  ├─ transactions/
│  └─ accounts/
```

## Decisões técnicas relevantes

- `UserProfile` (OneToOne com `User`) contém `role` e `host` para controlar escopo e
  permissões sem alterar o modelo de usuário padrão do Django.
- `HostAndRoleBasedScopeMixin` centraliza o filtro por `profile.host` em viewsets.
- Validações críticas (por exemplo, impedir venda acima do disponível) são tratadas
  nos serializers para retornar respostas HTTP 400 com mensagens legíveis.

---

Se quiser, posso também:

- adicionar um arquivo `.env.example` no repositório (arquivo sem segredos),
- atualizar o `.gitignore` para garantir que `.env` não seja versionado,
- e adicionar instruções para CI sobre como fornecer `SECRET_KEY` e outras
  variáveis sensíveis.

## CI (GitHub Actions) — como fornecer `SECRET_KEY` e outras variáveis sensíveis

Ao rodar o projeto em CI/runner (por exemplo GitHub Actions) você NÃO deve usar
um arquivo `.env`. Em vez disso, registre valores sensíveis como *Secrets* do
repositório e referencie-os nas jobs do workflow.

Passos recomendados:

1. No GitHub: vá em Settings -> Secrets and variables -> Actions -> New repository secret.
   - Adicione `SECRET_KEY` e quaisquer outras variáveis necessárias (ex.: `DATABASE_URL`,
     `DJANGO_ALLOWED_HOSTS`, `EMAIL_HOST_PASSWORD`, etc.).

2. (Opcional) Usar o GitHub CLI para criar secrets localmente:

   - Em Bash / Linux / macOS (exemplo gerando uma secret Django automaticamente):

   ```bash
   printf '%s' "$(python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
)" | gh secret set SECRET_KEY
   ```

   - Em PowerShell (Windows) com o venv ativado:

   ```powershell
   $k = .\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   gh secret set SECRET_KEY --body $k
   ```

3. No seu workflow do GitHub Actions, injete os secrets como variáveis de ambiente
   para a job que roda os testes / deploy. Exemplo mínimo de job que roda testes:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      # Disponibiliza as secrets como variáveis de ambiente dentro da job
      SECRET_KEY: ${{ secrets.SECRET_KEY }}
      # Outros exemplos: DATABASE_URL: ${{ secrets.DATABASE_URL }}
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install -r requirements.txt
      - name: Run tests
        run: |
          cd app
          python -m pytest -q
```

Boas práticas

- Nunca escreva secrets nos artefatos de workflow ou nos logs (evite `echo $SECRET_KEY`).
- Nomeie as secrets de forma explícita (`SECRET_KEY`, `DATABASE_URL`) e documente-as no README.
- Para deploys, prefira usar o mecanismo de secrets do provedor (AWS Secrets Manager,
  Google Secret Manager, HashiCorp Vault) em vez de variáveis de ambiente simples,
  quando a infraestrutura suportar.
