# [SPRINT 1 - T020] Módulo SMTP: Envío automatizado de correos.
# [SPRINT 1 - T019] Flujo de Recuperación de credenciales.
# [CU-03] Recuperación de Credenciales.
"""
Vistas para la recuperación de contraseña vía email.
Utiliza el sistema de tokens de Django para generar enlaces seguros de un solo uso.
"""

import logging
import smtplib

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.models import Usuario

logger = logging.getLogger(__name__)


class PasswordResetRequestAPIView(APIView):
    """[SPRINT 1 - T019] [T020] [CU-03] Solicitud de restablecimiento de contraseña."""

    permission_classes = [AllowAny]  # Endpoint público (el usuario no está logueado)

    def post(self, request):
        """Procesa la solicitud de restablecimiento enviando un email con token seguro."""
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "El campo email es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = Usuario.objects.get(email=email)  # pylint: disable=no-member
        except Usuario.DoesNotExist:  # pylint: disable=no-member
            # [T026] Seguridad: No revelar si el email existe o no
            logger.warning(
                "SECURITY: Intento de reset para email inexistente: %s",
                email,
            )
            return Response(
                {
                    "message": "Si el correo existe, recibirás un enlace de recuperación."
                },
                status=status.HTTP_200_OK,
            )

        # Generar token seguro de un solo uso
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # [T020] Enviar correo electrónico (o imprimirlo en consola en desarrollo)
        reset_url = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"
        try:
            send_mail(
                subject="PsicoSystem - Recuperación de Contraseña",
                message=(
                    f"Hola {user.username},\n\n"
                    f"Has solicitado restablecer tu contraseña.\n"
                    f"Usa este enlace: {reset_url}\n\n"
                    f"Si no solicitaste esto, ignora este correo.\n"
                    f"Este enlace expira en 24 horas."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info("AUTH: Email de recuperación enviado a %s", email)
        except (smtplib.SMTPException, OSError) as exc:
            logger.error("SMTP: Error al enviar correo a %s: %s", email, exc)

        return Response(
            {"message": "Si el correo existe, recibirás un enlace de recuperación."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    """[SPRINT 1 - T019] [T020] [CU-03] Confirmación de restablecimiento de contraseña."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Valida uid/token y establece la nueva contraseña."""
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([uid, token, new_password]):
            return Response(
                {"error": "uid, token y new_password son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = Usuario.objects.get(pk=user_id)  # pylint: disable=no-member
        except (TypeError, ValueError, Usuario.DoesNotExist):  # pylint: disable=no-member
            return Response(
                {"error": "Enlace de recuperación inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "El token ha expirado o ya fue utilizado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validación mínima de contraseña
        if len(new_password) < 8:
            return Response(
                {"error": "La contraseña debe tener al menos 8 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        logger.info(
            "AUTH: Contraseña restablecida exitosamente para %s",
            user.username,
        )

        return Response(
            {"message": "Contraseña restablecida exitosamente."},
            status=status.HTTP_200_OK,
        )
