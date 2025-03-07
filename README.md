# Service de Superposition Vidéo

Ce service permet de superposer automatiquement une vidéo principale sur une vidéo mockup, en redimensionnant et centrant la vidéo principale.

## Fonctionnalités

- Redimensionnement automatique de la vidéo principale à 80%
- Centrage de la vidéo sur le mockup
- Ajustement de la durée du mockup
- Format de sortie MP4 optimisé

## Configuration sur Render

1. Créer un nouveau Web Service
2. Sélectionner ce dépôt GitHub
3. Choisir l'environnement Docker
4. Sélectionner le plan gratuit
5. Cliquer sur "Create Web Service"

## Utilisation de l'API

### Endpoint de traitement vidéo

```
POST /process-video
Content-Type: multipart/form-data

Form fields:
- main_video: [fichier vidéo principal]
- mockup_video: [fichier vidéo mockup]
```

### Réponse

```json
{
  "success": true,
  "video_url": "https://votre-service.onrender.com/videos/output_1646432789.mp4",
  "message": "Vidéo traitée avec succès"
}
```

## Limitations

- Service gratuit Render : 512 MB RAM
- Stockage temporaire des fichiers
- Durée de la vidéo mockup ajustée à celle de la vidéo principale