import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We want to find PasarelaPagoMobileAPIView and insert the notification logic right before it returns.

old_logic = '''        # 3. Auditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Pago móvil registrado ({monto_decimal} BOB) para el paciente {paciente.nombre}"
        )

        return Response({'''

new_logic = '''        # 3. Auditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Pago móvil registrado ({monto_decimal} BOB) para el paciente {paciente.nombre}"
        )

        # 4. Enviar Notificación Push (Simulada para la Defensa)
        dispositivos = DispositivoMovil.objects.filter(usuario=request.user)
        for dispositivo in dispositivos:
            # Aquí iría la lógica real de firebase-admin. Ej: messaging.send(...)
            print(f"\\n[FIREBASE PUSH SIMULATOR] Enviando notificación de Pago Exitoso al token: {dispositivo.fcm_token}")
            print(f"[FIREBASE PUSH SIMULATOR] Titulo: Pago Aprobado")
            print(f"[FIREBASE PUSH SIMULATOR] Cuerpo: Su pago de {monto_decimal} BOB ha sido procesado con éxito.\\n")

        return Response({'''

if '[FIREBASE PUSH SIMULATOR]' not in content:
    content = content.replace(old_logic, new_logic)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added push notification simulation")
else:
    print("Simulation already exists")
