"""Configurações do Django.

As principais configurações são lidas de variáveis de ambiente. Para
desenvolvimento local, é possível definir um arquivo `.env` na raiz do
repositório (ex.: `.env`) com valores padrão.
"""

from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured

try:
    from dotenv import load_dotenv

    _HAS_DOTENV = True
except Exception:
    # python-dotenv não instalado: a aplicação continua; variáveis virão do
    # ambiente do sistema. Em CI/produção é esperado que as variáveis estejam
    # definidas no ambiente.
    _HAS_DOTENV = False

    def load_dotenv(*args, **kwargs):
        return None


BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do arquivo .env na raiz do repositório (opcional)
if _HAS_DOTENV:
    load_dotenv(BASE_DIR.parent.parent / ".env")


# DEBUG controla comportamento de debug/registro e exposição de endpoints de teste
DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")


# Chave secreta: prefer usar variável de ambiente em vez de hardcode.
# Em produção (DEBUG=False) exigimos que a variável de ambiente esteja definida
# e falhamos explicitamente para evitar exposição de segredos no código.
# Em desenvolvimento (DEBUG=True) mantemos um fallback inseguro apenas para
# conveniência local, mas não deve ser usado em deploys.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Fallback para desenvolvimento local
        SECRET_KEY = "django-insecure-dev-secret-key-placeholder"
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY não encontrada. Defina a variável de ambiente SECRET_KEY "
            "para ambientes de produção."
        )


ALLOWED_HOSTS: list[str] = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.portifolios",
    "apps.assets",
    "apps.holdings",
    "apps.transactions",
    "apps.accounts",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "core.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "core.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarity"
            "Validator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "pt-br"


TIME_ZONE = "America/Sao_Paulo"


USE_I18N = True


USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 10,
}
