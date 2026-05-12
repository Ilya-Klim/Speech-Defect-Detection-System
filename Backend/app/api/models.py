from pydantic import BaseModel
from typing import Optional, List


class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    problematic_sounds: Optional[List[str]] = None


class HealthResponse(BaseModel):
    status: str