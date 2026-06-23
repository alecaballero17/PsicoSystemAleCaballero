import sys

view_code = """
from rest_framework.permissions import AllowAny

class ClinicaPublicListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        clinicas = Clinica.objects.all().values("id", "nombre", "direccion", "plan_suscripcion")
        resultado = []
        for c in clinicas:
            especialidades = "Psicología General"
            if c["plan_suscripcion"] == "Premium":
                especialidades = "Psicología General, Psiquiatría, Terapia Familiar"
            elif c["plan_suscripcion"] == "Profesional":
                especialidades = "Psicología General, Terapia de Pareja"
                
            psicologos_count = Usuario.objects.filter(clinica_id=c["id"], rol="PSICOLOGO").count()
            
            plan_beneficios = "Gestión básica de citas y pacientes."
            horario = "Lunes a Viernes, 09:00 - 18:00"
            if c["plan_suscripcion"] == "Profesional":
                plan_beneficios = "Soporte Prioritario, múltiples agendas, Análisis Básico."
                horario = "Lunes a Sábado, 08:00 - 20:00"
            elif c["plan_suscripcion"] == "Premium":
                plan_beneficios = "Análisis IA Avanzado, Reportes Predictivos, Soporte VIP."
                horario = "Atención 24/7 (Citas de Emergencia Disponibles)"
            
            resultado.append({
                "id": c["id"],
                "nombre": c["nombre"],
                "direccion": c["direccion"] if c["direccion"] else "Dirección no registrada",
                "especialidades": especialidades,
                "plan_suscripcion": c["plan_suscripcion"],
                "psicologos_count": psicologos_count,
                "plan_beneficios": plan_beneficios,
                "horario": horario
            })
            
        return Response(resultado, status=status.HTTP_200_OK)
"""

with open('apps/P1_Identidad_Acceso/views.py', 'a', encoding='utf-8') as f:
    f.write("\n" + view_code)
print("Added ClinicaPublicListAPIView")
