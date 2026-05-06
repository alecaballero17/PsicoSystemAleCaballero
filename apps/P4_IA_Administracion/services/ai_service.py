import google.generativeai as genai
from django.conf import settings
from decouple import config

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
