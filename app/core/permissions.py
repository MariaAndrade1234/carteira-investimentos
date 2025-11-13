from rest_framework import permissions
from typing import Any


class IsAdminSuper(permissions.BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role == profile.ROLE_ADMIN_SUPER)


class IsInvestorSeniorSameHost(permissions.BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return False
        return profile.role == profile.ROLE_INVESTIDOR_SENIOR


class ReadOnlyForJunior(permissions.BasePermission):
    """Permissão que permite apenas leitura para INVESTIDOR_JUNIOR.

    Investidor junior recebe apenas métodos seguros (GET/HEAD/OPTIONS).
    """

    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return False
        if profile.role == profile.ROLE_INVESTIDOR_JUNIOR:
            return request.method in permissions.SAFE_METHODS
        return True


class IsSeniorOrAdmin(permissions.BasePermission):
    """Permissão que permite INVESTIDOR_SENIOR (mesmo host)
    ou ADMIN_SUPER escrever.

    """

    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return False
        if profile.role == profile.ROLE_ADMIN_SUPER:
            return True
        if profile.role == profile.ROLE_INVESTIDOR_SENIOR:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """ADMIN_SUPER permite acesso.

        INVESTIDOR_SENIOR permite somente para o mesmo host.

        `obj` pode ser um Portfolio ou um objeto relacionado a Portfolio/Holding.
        """
        profile = getattr(request.user, "profile", None)
        if not profile:
            return False
        if profile.role == profile.ROLE_ADMIN_SUPER:
            return True

        if profile.role != profile.ROLE_INVESTIDOR_SENIOR:
            return False

        obj_host = None
        if hasattr(obj, "host"):
            obj_host = getattr(obj, "host")
        else:
            portfolio = getattr(obj, "portfolio", None) or getattr(obj, "holding", None)
            if portfolio is not None:
                if hasattr(portfolio, "host"):
                    obj_host = getattr(portfolio, "host")
                elif hasattr(portfolio, "portfolio") and hasattr(
                    portfolio.portfolio, "host"
                ):
                    obj_host = getattr(portfolio.portfolio, "host")

        return obj_host == profile.host


class HostAndRoleBasedScopeMixin:
    """Mixin que aplica escopo por `host` conforme o perfil do usuário.

    - ADMIN_SUPER: vê todos os registros
    - INVESTIDOR_SENIOR/JUNIOR: filtra por `profile.host`
    """

    def get_queryset(self: Any) -> Any:  # type: ignore[misc]
        # Este mixin destina-se a ser usado em viewsets do Django, onde
        # `super().get_queryset()` e `self.request` existem. Anotamos
        # `self` como Any para satisfazer o verificador de tipos.
        qs = super().get_queryset()  # type: ignore[call-arg,misc]
        user = getattr(self.request, "user", None)
        profile = getattr(user, "profile", None)
        if profile is None:
            return qs.none()
        if profile.role == profile.ROLE_ADMIN_SUPER:
            return qs

        return qs.filter(host=profile.host)
