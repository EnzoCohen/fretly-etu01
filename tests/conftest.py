import os

# Base SQLite jetable et clé d'API de test, posées AVANT l'import de l'application
os.environ["DATABASE_URL"] = "sqlite:///./test_fretly.db"
os.environ["API_KEY"] = "cle-de-test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth():
    return {"X-API-Key": "cle-de-test"}
