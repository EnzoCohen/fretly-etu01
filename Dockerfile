# syntax=docker/dockerfile:1

# Étape 1 : installation des dépendances dans un environnement virtuel
FROM python:3.12.13-alpine3.23 AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-compile -r requirements.txt \
    && pip uninstall -y pip


# Étape 2 : image finale, uniquement ce qu'il faut pour exécuter l'API
FROM python:3.12.13-alpine3.23

ARG GIT_COMMIT=unknown
ARG APP_VERSION=1.4.0

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION} \
    GIT_COMMIT=${GIT_COMMIT}

LABEL org.opencontainers.image.source="https://github.com/EnzoCohen/fretly-etu01" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

# Mise à jour des paquets système (correctifs de sécurité) et création de l'utilisateur
RUN apk upgrade --no-cache \
    && addgroup -S -g 10001 fretly \
    && adduser -S -D -H -u 10001 -G fretly -s /sbin/nologin fretly

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/

USER fretly

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
