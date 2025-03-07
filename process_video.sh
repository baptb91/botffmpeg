#!/bin/bash

MAIN_VIDEO=$1
MOCKUP_VIDEO=$2
OUTPUT_VIDEO=$3

# Logging
echo "Début du traitement vidéo"
echo "Vidéo principale: $MAIN_VIDEO"
echo "Vidéo mockup: $MOCKUP_VIDEO"
echo "Fichier de sortie: $OUTPUT_VIDEO"

# Vérifier la présence des fichiers
if [ ! -f "$MAIN_VIDEO" ] || [ ! -f "$MOCKUP_VIDEO" ]; then
    echo "Erreur: Un ou plusieurs fichiers d'entrée manquants"
    exit 1
fi

# Vérifier si ffmpeg est installé
if ! command -v ffmpeg &> /dev/null; then
    echo "Erreur: ffmpeg n'est pas installé"
    exit 1
fi

# Obtenir la durée de la vidéo principale
echo "Vérification de la durée de la vidéo principale..."
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$MAIN_VIDEO")

if [ $? -ne 0 ]; then
    echo "Erreur lors de la lecture de la durée de la vidéo"
    exit 1
fi

echo "Durée de la vidéo: $DURATION secondes"

# Traiter les vidéos avec ffmpeg
echo "Début du traitement ffmpeg..."
ffmpeg -i "$MAIN_VIDEO" -i "$MOCKUP_VIDEO" -filter_complex \
"[0:v]scale=iw*0.8:ih*0.8[scaled]; \
 [1:v]trim=0:$DURATION[trimmed]; \
 [trimmed][scaled]overlay=(W-w)/2:(H-h)/2:shortest=1" \
-c:v libx264 -preset ultrafast -crf 28 \
-c:a aac -b:a 128k \
"$OUTPUT_VIDEO" 2>&1

# Vérifier si le fichier de sortie a été créé
if [ -f "$OUTPUT_VIDEO" ]; then
    echo "Traitement terminé avec succès: $OUTPUT_VIDEO"
    exit 0
else
    echo "Erreur: Le fichier de sortie n'a pas été créé"
    exit 1
fi
