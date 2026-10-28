"""Schémas d'entrée / sortie de l'API (Pydantic v2)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShipmentIn(BaseModel):
    reference: str = Field(min_length=3, max_length=20)
    recipient: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=80)
    weight_kg: float = Field(gt=0, le=1000)
    distance_km: float = Field(gt=0, le=5000)
    express: bool = False


class ShipmentOut(ShipmentIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    price_eur: float = 0.0
    created_at: datetime


class StatusUpdate(BaseModel):
    status: str
