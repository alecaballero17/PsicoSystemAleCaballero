"""
[SPRINT 1 - T018] Middleware RBAC: Control de acceso basado en roles.
[RF-28] Restricción de acceso a módulos por rol asignado.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """[SPRINT 1 - T018] [RF-28] Solo usuarios con rol ADMIN."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == "ADMIN"
        )


class IsPsicologo(BasePermission):
    """[SPRINT 1 - T018] [RF-28] Acceso para PSICOLOGO y ADMIN."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol in ["ADMIN", "PSICOLOGO"]
        )
