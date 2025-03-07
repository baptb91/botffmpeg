#!/bin/bash

MAIN_VIDEO=$1
MOCKUP_VIDEO=$2
OUTPUT_VIDEO=$3

# Vérifier la présence des fichiers
if [ ! -f "$MAIN_VIDEO" ] || [ ! -f "$MOCKUP_VIDEO" ]; then
    echo "Erreur: Un ou plusieurs fichiers d'entrée manquants"
    exit 1
fi

# Obtenir la durée de la vidéo principale
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$MAIN_VIDEO")

# Traiter les vidéos avec ffmpeg
ffmpeg -i "$MAIN_VIDEO" -i "$MOCKUP_VIDEO" -filter_complex \
"[0:v]scale=iw*0.8:ih*0.8[scaled]; \
 [1:v]trim=0:$DURATION[trimmed]; \
 [trimmed][scaled]overlay=(W-w)/2:(H-h)/2:shortest=1" \
-c:v libx264 -preset faster -crf 23 \
-c:a aac -b:a 128k \
"$OUTPUT_VIDEO"

# Vérifier si le fichier de sortie a été créé
if [ -f "$OUTPUT_VIDEO" ]; then
    echo "Traitement terminé avec succès: $OUTPUT_VIDEO"
    exit 0
else
    echo "Erreur: Le fichier de sortie n'a pas été créé"
    exit 1
fi