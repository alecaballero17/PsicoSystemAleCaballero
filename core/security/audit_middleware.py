# [SPRINT 1 - T023] Logging y Auditoría: Trazas de eventos para registrar accesos.
# [RF-30] Registro de Auditoría: Logs de eventos críticos.
"""
Middleware de auditoría que registra todos los eventos de acceso a la API.
Captura: IP de origen, usuario, método HTTP, endpoint, código de respuesta.
"""

import logging
import time

logger = logging.getLogger("audit")


class AuditLogMiddleware:
    """[SPRINT 1 - T023] [RF-30] Middleware de auditoría para trazabilidad de accesos."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capturar timestamp de inicio
        start_time = time.time()

        # Procesar la request
        response = self.get_response(request)

        # Calcular duración
        duration = time.time() - start_time

        # Solo registrar peticiones a la API (ignorar admin y estáticos)
        if request.path.startswith("/api/"):
            user = (
                request.user.username
                if hasattr(request, "user") and request.user.is_authenticated
                else "ANÓNIMO"
            )
            ip = self._get_client_ip(request)

            logger.info(
                f"AUDIT | {request.method} {request.path} | "
                f"User: {user} | IP: {ip} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s"
            )

        return response

    @staticmethod
    def _get_client_ip(request):
        """Extrae la IP real del cliente, considerando proxies reversos."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "UNKNOWN")
