import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\urls.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'RegistroTokenFCMAPIView' not in content:
    content = content.replace(
        'PasarelaPagoMobileAPIView\n)',
        'PasarelaPagoMobileAPIView,\n    RegistroTokenFCMAPIView\n)'
    )
    content = content.replace(
        'path("api/mobile/paciente/pagar/", PasarelaPagoMobileAPIView.as_view(), name="api_mobile_pagar"),\n]',
        'path("api/mobile/paciente/pagar/", PasarelaPagoMobileAPIView.as_view(), name="api_mobile_pagar"),\n    path("api/mobile/notificaciones/registrar-token/", RegistroTokenFCMAPIView.as_view(), name="api_mobile_fcm_token"),\n]'
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added URL")
else:
    print("URL already exists")
