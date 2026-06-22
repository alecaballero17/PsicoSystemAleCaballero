import google.generativeai as genai
from groq import Groq
from django.conf import settings
from decouple import config
import requests
import json
import datetime

class AIService:
    @staticmethod
    def responder_chatbot(context_prompt, user_message):
        """
        Envía un mensaje al modelo de Groq utilizando un contexto previo (system prompt).
        """
        api_key = config("GROQ_API_KEY", default=None)
        if not api_key:
            return "ERROR: Groq API Key no configurada en las variables de entorno."

        try:
            client = Groq(api_key=api_key.strip("'\""))
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": context_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                stream=False
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Lo siento, ocurrió un error procesando tu solicitud: {str(e)}"
    @staticmethod
    def transcribir_audio_groq(file_obj, filename):
        """
        Transcribe un archivo de audio usando el modelo whisper de Groq.
        """
        api_key = config("GROQ_API_KEY", default=None)
        if not api_key:
            return {"error": "Groq API Key no configurada."}
            
        try:
            # Eliminamos posibles comillas de la variable de entorno
            api_key = api_key.strip("'\"")
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            files = {
                "file": (filename, file_obj)
            }
            data = {
                "model": "whisper-large-v3",
                "language": "es",
                "temperature": "0.0",
                "response_format": "json"
            }
            response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data)
            response.raise_for_status()
            
            transcription = response.json()
            return {"text": transcription.get("text", "")}
        except Exception as e:
            return {"error": f"Error transcribiendo audio con Groq: {str(e)}"}

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
        en la base de datos de la clínica. Usa Groq LLM (llama3-8b-8192) para mayor velocidad y gratuidad.
        """
        api_key = config("GROQ_API_KEY", default=None)
        if not api_key:
            return {"error": "Groq API Key no configurada."}

        try:
            client = Groq(api_key=api_key.strip("'\""))
            hoy = datetime.datetime.now()
            
            system_prompt = f"""
            Eres un asistente de base de datos para una clínica. Tu tarea es extraer filtros 
            de un comando de voz en lenguaje natural y devolver ÚNICAMENTE un objeto JSON válido, sin Markdown ni texto adicional.
            
            Fecha actual como referencia: {hoy.strftime('%Y-%m-%d')}
            
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
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Comando de voz transcrito: '{transcript}'"}
                ],
                temperature=0.1,
                max_tokens=256,
                response_format={"type": "json_object"}
            )
            
            text = completion.choices[0].message.content.strip()
            return json.loads(text)
        except Exception as e:
            return {"error": f"Error interpretando comando con Groq: {str(e)}"}
