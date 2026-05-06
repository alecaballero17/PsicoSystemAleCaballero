from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    @staticmethod
    def enviar_notificacion(asunto, mensaje, destinatario):
        try:
            send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [destinatario], fail_silently=False)
            return True
        except Exception as e:
            print(f'Error enviando notificacion: {e}')
            return False

    @staticmethod
    def notificar_registro_paciente(paciente):
        asunto = f'Bienvenido a {paciente.clinica.nombre}'
        mensaje = f'Hola {paciente.nombre}, has sido registrado exitosamente.'
        return NotificationService.enviar_notificacion(asunto, mensaje, 'paciente@ejemplo.com')
