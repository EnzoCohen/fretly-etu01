"""Calcul du prix d'une expédition et cycle de vie des statuts."""
import math

BASE_FEE = 4.90           # frais fixes (EUR)
PRICE_PER_KG = 0.80       # EUR par kg
PRICE_PER_KM = 0.05       # EUR par km
EXPRESS_SURCHARGE = 0.30  # +30 % sur le total en express
MIN_PRICE = 6.00

# Transitions autorisées : statut actuel -> statuts suivants possibles
TRANSITIONS = {
    "CREATED": {"IN_TRANSIT", "CANCELLED"},
    "IN_TRANSIT": {"DELIVERED", "RETURNED"},
    "DELIVERED": set(),
    "RETURNED": set(),
    "CANCELLED": set(),
}


def compute_price(weight_kg: float, distance_km: float, express: bool = False) -> float:
    """Prix TTC arrondi au centime."""
    price = BASE_FEE + weight_kg * PRICE_PER_KG + distance_km * PRICE_PER_KM
    if express:
        price = price + EXPRESS_SURCHARGE
    return round(max(price, MIN_PRICE), 2)


def can_transition(current: str, new: str) -> bool:
    return new in TRANSITIONS.get(current, set())
