import google.generativeai as genai
from django.conf import settings
from decouple import config
import json
import datetime

class AIService:
    @staticmethod
    def analizar_nota_clinica(nota_texto):
        """
        Analiza una nota de evolución clínica y devuelve un diagnóstico predictivo
        o sugerencias médicas.
        """
        api_key = config("GOOGLE_API_KEY", default=None)
        if not api_key:
            return "ERROR: Google API Key no configurada."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Eres un asistente de inteligencia artificial especializado en psicología clínica.
            Analiza la siguiente nota de sesión de un paciente y proporciona:
            1. Un resumen ejecutivo del estado emocional.
            2. Un diagnóstico predictivo preliminar (basado solo en la nota).
            3. Sugerencias para la próxima sesión.

            NOTA DE SESIÓN:
            {nota_texto}
            
            Responde en formato de texto claro y profesional.
            """
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error en el análisis de IA: {str(e)}"

    @staticmethod
    def interpretar_comando_voz(transcript):
        """
        Recibe un texto transcrito por voz y extrae filtros estructurados para consultas
        en la base de datos de la clínica.
        """
        api_key = config("GOOGLE_API_KEY", default=None)
        if not api_key:
            return {"error": "Google API Key no configurada."}

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            hoy = datetime.datetime.now()
            
            prompt = f"""
            Eres un asistente de base de datos para una clínica. Tu tarea es extraer filtros 
            de un comando de voz en lenguaje natural y devolver ÚNICAMENTE un objeto JSON válido, sin Markdown.
            
            Fecha actual como referencia: {hoy.strftime('%Y-%m-%d')}
            
            Comando de voz transcrito: "{transcript}"
            
            Filtros que puedes extraer (si el usuario no los menciona, déjalos como null):
            - "fecha_inicio" (YYYY-MM-DD): Ejemplo "desde enero", "este mes".
            - "fecha_fin" (YYYY-MM-DD): Ejemplo "hasta marzo".
            - "estado_cita": Puede ser "PENDIENTE", "COMPLETADA", "CANCELADA" o "NO_ASISTIO".
            - "monto_min": Número (ej: pagos mayores a 100).
            - "monto_max": Número.
            - "top_psicologo": booleano (true si pregunta por el psicólogo con más citas).
            
            Ejemplo de salida JSON puro:
            {{
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-03-31",
                "estado_cita": "CANCELADA",
                "monto_min": null,
                "monto_max": null,
                "top_psicologo": false
            }}
            """
            
            response = model.generate_content(prompt)
            # Limpiar posible markdown (```json ... ```)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            return json.loads(text.strip())
        except Exception as e:
            return {"error": f"Error interpretando comando: {str(e)}"}
