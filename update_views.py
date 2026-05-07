import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\views.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    'from apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador, EsPsicologoOAdministrador',
    'import requests\nfrom apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador, EsPsicologoOAdministrador, RequiresModuloContabilidad, RequiresModuloIA'
)

# 2. Update Contabilidad Permissions
content = content.replace(
    'permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador]',
    'permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloContabilidad]'
)

# Fix the specific permission for AnalisisIAView to use RequiresModuloIA instead
content = content.replace(
    'class AnalisisIAView(APIView):\n    """\n    Endpoint para disparar el análisis de IA sobre una nota de evolución.\n    """\n    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloContabilidad]',
    'class AnalisisIAView(APIView):\n    """\n    Endpoint para disparar el análisis de IA llamando al Microservicio FastAPI.\n    """\n    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloIA]'
)

# Fix logic for AnalisisIAView to call microservice
old_ia_post = '''    def post(self, request, evolucion_id):
        evolucion = get_object_or_404(
            EvolucionClinica, 
            id=evolucion_id, 
            historia__paciente__clinica=request.user.clinica
        )
        
        if not evolucion.notas_sesion:
            return Response(
                {"error": "La nota de sesión está vacía."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = AIService.analizar_nota_clinica(evolucion.notas_sesion)
        evolucion.analisis_ia = resultado
        evolucion.save()

        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Ejecutó análisis de IA para la sesión de: {evolucion.historia.paciente.nombre}"
        )

        return Response({"analisis_ia": resultado}, status=status.HTTP_200_OK)'''

new_ia_post = '''    def post(self, request, evolucion_id):
        evolucion = get_object_or_404(
            EvolucionClinica, 
            id=evolucion_id, 
            historia__paciente__clinica=request.user.clinica
        )
        
        if not evolucion.notas_sesion:
            return Response(
                {"error": "La nota de sesión está vacía."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Llamada al Microservicio Externo
        try:
            response = requests.post(
                "http://127.0.0.1:8001/api/v1/analyze",
                json={"notas": evolucion.notas_sesion},
                timeout=5
            )
            response.raise_for_status()
            resultado = response.json()
            evolucion.analisis_ia = str(resultado)
            evolucion.save()
        except Exception as e:
            return Response(
                {"error": f"Error del Microservicio de IA: {str(e)}"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Ejecutó análisis de IA (Vía Microservicio) para la sesión de: {evolucion.historia.paciente.nombre}"
        )

        return Response({"analisis_ia": resultado}, status=status.HTTP_200_OK)'''

content = content.replace(old_ia_post, new_ia_post)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Success updating views.py')
