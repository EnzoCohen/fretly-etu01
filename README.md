# Fretly API

API de suivi d'expéditions de la société **Fretly** (transport de colis entre professionnels).

## Stack

- Python 3.12, FastAPI, SQLAlchemy 2
- PostgreSQL en production, SQLite en développement
- Tests : pytest ; lint : ruff

## Lancer en local sans Docker

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
API_KEY=dev uvicorn app.main:app --reload
```

Documentation interactive : http://localhost:8000/docs

## Tests et lint

```bash
pytest
ruff check .
```

## Routes

| Méthode | Route                    | Clé d'API | Rôle                                       |
| ------- | ------------------------ | --------- | ------------------------------------------ |
| GET     | `/health`                | non       | État de l'API et de la base                |
| GET     | `/version`               | non       | Version et commit déployés                 |
| GET     | `/shipments`             | non       | Liste des expéditions                      |
| GET     | `/shipments/{id}`        | non       | Détail d'une expédition (avec prix)        |
| POST    | `/shipments`             | oui       | Créer une expédition                       |
| PATCH   | `/shipments/{id}/status` | oui       | Changer le statut                          |
| POST    | `/shipments/import`      | oui       | Import CSV (voir `data/colis-exemple.csv`) |

La clé d'API se passe dans l'en-tête `X-API-Key`.

## Variables d'environnement

| Variable       | Défaut                    | Rôle                                 |
| -------------- | ------------------------- | ------------------------------------ |
| `DATABASE_URL` | `sqlite:///./fretly.db`   | Chaîne de connexion SQLAlchemy       |
| `API_KEY`      | (vide : écriture refusée) | Clé exigée sur les routes d'écriture |
| `APP_ENV`      | `development`             | Nom de l'environnement               |
| `APP_VERSION`  | `0.0.0-dev`               | Version affichée par `/version`      |
| `GIT_COMMIT`   | `unknown`                 | Commit affiché par `/version`        |

## Stratégie de branches

J'ai choisi **GitHub Flow** :

- `main` est la seule branche permanente. Elle doit toujours être stable, puisque chaque push sur `main` part en production.
- Chaque évolution se fait sur une branche courte créée depuis `main` (`feature/docker`, `feature/ci`, `feature/deploy`…), puis revient dans `main` par une Pull Request une fois la CI verte.
- On ne pousse jamais directement sur `main` : c'est bloqué par un ruleset.

Pourquoi pas GitFlow ? Je travaille seul sur le projet et il n'y a qu'un seul environnement (le serveur EC2). Une branche `develop` et des branches de release ajouteraient des fusions en plus sans rien apporter. Avec GitHub Flow, le chemin est simple : une branche, une PR, la CI vérifie, on fusionne, et le déploiement part tout seul depuis `main`.
