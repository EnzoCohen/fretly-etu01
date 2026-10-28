"""Fretly API : suivi d'expéditions."""
import csv
import io
import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import Base, engine, get_db
from app.pricing import can_transition, compute_price
from app.schemas import ShipmentIn, ShipmentOut, StatusUpdate
from app.security import require_api_key


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Fretly API", version=settings.app_version, lifespan=lifespan)


def to_out(s: models.Shipment) -> ShipmentOut:
    out = ShipmentOut.model_validate(s)
    out.price_eur = compute_price(s.weight_kg, s.distance_km, s.express)
    return out


def find_by_reference(db: Session, reference: str):
    return db.scalar(select(models.Shipment).where(models.Shipment.reference == reference))


@app.get("/")
def root():
    return {"service": "fretly-api", "docs": "/docs"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error", "database": "down"})
    return {"status": "ok", "database": "up"}


@app.get("/version")
def version():
    return {"version": settings.app_version, "commit": settings.git_commit, "env": settings.app_env}


@app.get("/shipments", response_model=list[ShipmentOut])
def list_shipments(db: Session = Depends(get_db)):
    rows = db.scalars(select(models.Shipment).order_by(models.Shipment.id)).all()
    return [to_out(s) for s in rows]


@app.get("/shipments/{shipment_id}", response_model=ShipmentOut)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    s = db.get(models.Shipment, shipment_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Expédition introuvable")
    return to_out(s)


@app.post("/shipments", response_model=ShipmentOut, status_code=201,
          dependencies=[Depends(require_api_key)])
def create_shipment(payload: ShipmentIn, db: Session = Depends(get_db)):
    if find_by_reference(db, payload.reference):
        raise HTTPException(status_code=409, detail="Référence déjà utilisée")
    s = models.Shipment(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return to_out(s)


@app.patch("/shipments/{shipment_id}/status", response_model=ShipmentOut,
           dependencies=[Depends(require_api_key)])
def update_status(shipment_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    s = db.get(models.Shipment, shipment_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Expédition introuvable")
    if not can_transition(s.status, payload.status):
        raise HTTPException(status_code=422, detail=f"Transition {s.status} -> {payload.status} interdite")
    s.status = payload.status
    db.commit()
    db.refresh(s)
    return to_out(s)


@app.post("/shipments/import", dependencies=[Depends(require_api_key)])
async def import_shipments(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import en masse d'un CSV : reference;recipient;city;weight_kg;distance_km;express"""
    content = (await file.read()).decode("utf-8")
    created, errors = 0, []
    for line_no, row in enumerate(csv.DictReader(io.StringIO(content), delimiter=";"), start=2):
        express = (row.get("express") or "").strip().lower() in ("1", "true", "oui")
        try:
            data = ShipmentIn(**{**row, "express": express})
        except ValueError as exc:
            errors.append({"line": line_no, "error": str(exc).splitlines()[0]})
            continue
        if find_by_reference(db, data.reference):
            errors.append({"line": line_no, "error": "référence déjà utilisée"})
            continue
        db.add(models.Shipment(**data.model_dump()))
        created += 1
    db.commit()
    return {"created": created, "errors": errors}
