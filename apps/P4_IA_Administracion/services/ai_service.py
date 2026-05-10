import json
import datetime
import google.generativeai as genai
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

    @staticmethod
    def interpretar_comando_voz(transcript: str) -> dict:
        """
        Recibe texto dictado por voz y usa Gemini para extraer filtros estructurados.

        Filtros posibles (todos opcionales):
          - fecha_inicio / fecha_fin (YYYY-MM-DD)
          - estado_cita: PENDIENTE | COMPLETADA | CANCELADA | NO_ASISTIO
          - top_psicologo: true/false
          - monto_min / monto_max: decimales para filtrar transacciones

        Retorna un dict con los filtros extraídos o {"error": "..."} si falla.
        """
        api_key = config("GOOGLE_API_KEY", default=None)
        if not api_key:
            return {"error": "Google API Key no configurada."}

        hoy = datetime.date.today().isoformat()

        prompt = f"""
Hoy es {hoy}. Eres un asistente que extrae filtros de reportes clínicos a partir de texto dictado por voz.

A partir del siguiente texto, extrae los filtros que correspondan y devuelve ÚNICAMENTE un objeto JSON válido con estas claves exactas (omite las que no apliquen o déjalas null):

- "fecha_inicio": string formato YYYY-MM-DD o null
- "fecha_fin": string formato YYYY-MM-DD o null
- "estado_cita": uno de ["PENDIENTE","COMPLETADA","CANCELADA","NO_ASISTIO"] o null
- "top_psicologo": true si el usuario pide saber el psicólogo con más citas, sino false
- "monto_min": número decimal o null
- "monto_max": número decimal o null

Reglas de interpretación temporal:
- "este mes" = del primer día al último día del mes actual.
- "este año" = del 1 de enero al 31 de diciembre del año actual.
- "últimos 30 días" = desde hace 30 días hasta hoy.

Reglas de estado:
- "canceladas" / "cancelados" → estado_cita = "CANCELADA"
- "pendientes" → estado_cita = "PENDIENTE"
- "completadas" / "atendidas" → estado_cita = "COMPLETADA"
- "no asistió" / "ausentes" / "inasistencias" → estado_cita = "NO_ASISTIO"

Reglas de monto:
- "pagos mayores a X" → monto_min = X
- "pagos menores a X" → monto_max = X
- "entre X y Y bolivianos" → monto_min = X, monto_max = Y

Reglas de psicólogo:
- "psicólogo con más citas" / "especialista más activo" / "quien atendió más" → top_psicologo = true

TEXTO DICTADO: "{transcript}"

Responde SOLO con el JSON, sin explicaciones, sin markdown, sin bloques de código.
"""

        raw = ""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            raw = response.text.strip()
            # Limpiar posibles bloques de código que Gemini añada por error
            raw = raw.replace("```json", "").replace("```", "").strip()
            filtros = json.loads(raw)
            return filtros
        except json.JSONDecodeError:
            return {"error": f"Gemini no devolvió JSON válido. Respuesta: {raw[:300]}"}
        except Exception as e:
            return {"error": f"Error al interpretar comando de voz: {str(e)}"}
