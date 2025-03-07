FROM python:3.9-alpine

# Installer ffmpeg et dépendances système nécessaires
RUN apk add --no-cache \
    ffmpeg \
    bash \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev

# Créer dossiers de travail
WORKDIR /app
RUN mkdir -p /app/uploads /app/output

# Installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY . .

# Rendre le script exécutable
RUN chmod +x process_video.sh

# Exposer le port
EXPOSE 8080

# Démarrer l'application avec gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "300", "app:app"]
