FROM python:3.9-slim

# Installer ffmpeg et dépendances
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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

# Démarrer l'application
CMD ["python", "app.py"]