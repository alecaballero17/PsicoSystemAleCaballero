from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Permite acceso únicamente a los usuarios con rol de Administrador.
    Trazabilidad: RF-28 (Control de accesos)
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'ADMIN')

class IsPsicologo(BasePermission):
    """
    Permite acceso a Psicólogos y Administradores.
    Trazabilidad: RF-28 (Control de accesos)
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['ADMIN', 'PSICOLOGO']
        )
