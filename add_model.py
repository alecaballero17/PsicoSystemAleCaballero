import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P1_Identidad_Acceso\models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_model = '''
# ==============================================================================
# MÓDULO: NOTIFICACIONES PUSH (MÓVIL)
# ==============================================================================
class DispositivoMovil(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='dispositivos')
    fcm_token = models.CharField(max_length=255, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispositivo de {self.usuario.username}"
'''

if 'class DispositivoMovil' not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write('\n' + new_model)
    print("Added DispositivoMovil")
else:
    print("Already exists")
