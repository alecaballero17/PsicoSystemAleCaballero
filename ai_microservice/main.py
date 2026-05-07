from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import random

app = FastAPI(
    title="PsicoSystem AI Microservice",
    description="Microservicio independiente para análisis y diagnóstico predictivo con IA.",
    version="1.0.0"
)

class ClinicalNote(BaseModel):
    notas: str

class AIAnalysisResult(BaseModel):
    diagnostico_predictivo: str
    confianza: float
    recomendaciones: list[str]

@app.post("/api/v1/analyze", response_model=AIAnalysisResult)
async def analyze_clinical_notes(note: ClinicalNote):
    if not note.notas or len(note.notas.strip()) < 10:
        raise HTTPException(status_code=400, detail="La nota clínica es muy corta para un análisis preciso.")
    
    # Simulación de un retraso de procesamiento de IA
    time.sleep(1.5)
    
    texto = note.notas.lower()
    
    diagnostico = "Trastorno de Ansiedad Generalizada (Posible)"
    confianza = round(random.uniform(0.70, 0.95), 2)
    recomendaciones = [
        "Sugerir técnicas de respiración diafragmática.",
        "Evaluar calidad del sueño en la próxima sesión."
    ]
    
    if "depresión" in texto or "triste" in texto or "llanto" in texto:
        diagnostico = "Episodio Depresivo Leve a Moderado"
        recomendaciones = [
            "Realizar inventario de depresión de Beck.",
            "Explorar red de apoyo familiar."
        ]
    elif "estrés" in texto or "trabajo" in texto or "presión" in texto:
        diagnostico = "Estrés Laboral / Burnout"
        recomendaciones = [
            "Fomentar límites claros entre trabajo y descanso.",
            "Posible derivación a psiquiatría."
        ]
        
    return AIAnalysisResult(
        diagnostico_predictivo=diagnostico,
        confianza=confianza,
        recomendaciones=recomendaciones
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "AI Microservice is running"}
