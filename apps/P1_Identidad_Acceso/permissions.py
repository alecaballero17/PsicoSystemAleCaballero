"""Permisos DRF para RBAC y multi-tenant (acceso acotado por clínica)."""

from rest_framework import permissions


class HasClinicaAsignada(permissions.BasePermission):
    message = "Tu cuenta no tiene clínica asignada."

    def has_permission(self, request, view):
        u = request.user
        return bool(
            u and u.is_authenticated and getattr(u, "clinica_id", None) is not None
        )


class EsPsicologoOAdministrador(permissions.BasePermission):
    message = "Solo psicólogos o administradores pueden realizar esta acción."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        return getattr(u, "rol", None) in ("PSICOLOGO", "ADMIN")


class EsAdministrador(permissions.BasePermission):
    """Solo rol ADMIN explícito. is_superuser NO otorga acceso automático a la API."""

    message = "Solo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        # Bloquear superusuarios que no tengan rol ADMIN explícito
        return getattr(u, "rol", None) == "ADMIN"
