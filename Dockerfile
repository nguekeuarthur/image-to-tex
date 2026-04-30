FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Création d'un utilisateur non-root (recommandé par HF Spaces)
RUN useradd -m -u 1000 user

# Dépendances système nécessaires pour OpenCV (utilisé par EasyOCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

USER user
WORKDIR /home/user/app

# Installation des dépendances Python (couche cachée pour rebuild rapide)
COPY --chown=user requirements.txt .
RUN pip install --user -r requirements.txt

# Copie du code de l'app
COPY --chown=user . .

# Pré-téléchargement du modèle EasyOCR pour FR+EN au build
# Évite l'attente de 1-2 min au premier appel utilisateur
RUN python -c "import easyocr; easyocr.Reader(['fr', 'en'], gpu=False, verbose=False)"

# Port utilisé par HF Spaces
EXPOSE 7860

# Lancement avec gunicorn (production) au lieu du serveur de dev Flask
CMD ["gunicorn", "app:app", \
     "--workers", "1", \
     "--threads", "4", \
     "--timeout", "300", \
     "--bind", "0.0.0.0:7860"]
