"""Configuration de l'application, lue dans les variables d'environnement."""
import os


class Settings:
    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development")
        self.app_version = os.getenv("APP_VERSION", "0.0.0-dev")
        self.git_commit = os.getenv("GIT_COMMIT", "unknown")
        # En local : SQLite. En conteneur : PostgreSQL, par exemple
        # postgresql+psycopg://fretly:motdepasse@db:5432/fretly
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./fretly.db")
        # Clé exigée sur les routes d'écriture (en-tête X-API-Key)
        self.api_key = os.getenv("API_KEY", "")


settings = Settings()
