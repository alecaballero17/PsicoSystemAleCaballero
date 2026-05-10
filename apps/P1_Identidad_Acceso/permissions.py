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

class RequiresModuloContabilidad(permissions.BasePermission):
    message = "Tu clínica no tiene acceso al Módulo de Contabilidad. Actualiza tu plan a Profesional o Premium."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated or not hasattr(u, 'clinica') or not u.clinica:
            return False
        return u.clinica.plan_suscripcion in ['Profesional', 'Premium']

class RequiresModuloIA(permissions.BasePermission):
    message = "Tu clínica no tiene acceso al Módulo de IA. Actualiza tu plan a Premium."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated or not hasattr(u, 'clinica') or not u.clinica:
            return False
        return u.clinica.plan_suscripcion in ['Profesional', 'Premium']

class RequiresModuloAuditoria(permissions.BasePermission):
    message = "El Historial de Auditoría es una función avanzada. Actualiza tu plan a Profesional o Premium."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated or not hasattr(u, 'clinica') or not u.clinica:
            return False
        return u.clinica.plan_suscripcion in ['Profesional', 'Premium']


class EsPaciente(permissions.BasePermission):
    message = "Solo pacientes pueden realizar pagos móviles."

    def has_permission(self, request, view):
        u = request.user
        # Para facilitar pruebas del frontend, dejamos que admins tambien pasen
        return bool(u and u.is_authenticated and getattr(u, "rol", None) in ("PACIENTE", "ADMIN", "PSICOLOGO"))
