from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, File, HTTPException, UploadFile, Form
from loguru import logger

from Backend.app.api.models import PredictionResponse, HealthResponse
from Backend.app.services.preprocessing import preprocess_audio
from Backend.app.services.model_loader import load_model, load_scaler

router = APIRouter(prefix="/api/v1")

model = None
scaler = None

SOUNDS_MAP = {
    "рлш": ["р", "л", "ш"],
    "стр": ["с", "т", "р"],
    "трш": ["т", "р", "ш"],
    "стрлш": ["с", "т", "р", "л", "ш"],
    "чстрл": ["ч", "с", "т", "р", "л"],
}


def init_models():
    global model, scaler
    if model is None:
        model = load_model()
        scaler = load_scaler()
        logger.info("Модель и scaler загружены")


@router.get("/health", response_model=HealthResponse, status_code=HTTPStatus.OK)
async def health():
    return HealthResponse(status="ok")


@router.post("/predict", response_model=PredictionResponse, status_code=HTTPStatus.OK)
async def predict(
    file: Annotated[UploadFile, File(description="Аудиофайл (WAV, MP3, OGG)")],
    twister: Annotated[str, Form(description="Тип скороговорки")] = None,
):
    if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg')):
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")

    try:
        contents = await file.read()
        features = preprocess_audio(contents)
        if features.shape[0] != 255:
            raise HTTPException(status_code=500, detail="Ошибка извлечения признаков")

        features_scaled = scaler.transform([features])
        proba = model.predict_proba(features_scaled)[0, 1]
        pred_class = 1 if proba >= 0.5 else 0
        label = "плохо" if pred_class == 1 else "хорошо"

        problematic_sounds = None
        if pred_class == 1 and twister and twister in SOUNDS_MAP:
            problematic_sounds = SOUNDS_MAP[twister]

        return PredictionResponse(
            prediction=label, probability=float(proba), problematic_sounds=problematic_sounds
        )
    except Exception as e:
        logger.error(f"Ошибка при предсказании: {e}")
        raise HTTPException(status_code=500, detail=str(e))