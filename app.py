import os
import time
import subprocess
import logging
from flask import Flask, request, jsonify, send_file

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Augmenter la taille maximale des fichiers (500 MB)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

UPLOAD_FOLDER = '/app/uploads'
OUTPUT_FOLDER = '/app/output'

@app.route('/process-video', methods=['POST'])
def process_video():
    try:
        logger.info("Début du traitement de la requête")
        
        # Vérifier les fichiers
        if 'main_video' not in request.files or 'mockup_video' not in request.files:
            logger.error("Fichiers manquants dans la requête")
            return jsonify({'error': 'Les deux fichiers vidéo sont requis'}), 400
        
        # Récupérer les fichiers
        main_video = request.files['main_video']
        mockup_video = request.files['mockup_video']
        
        logger.info(f"Fichiers reçus: main={main_video.filename}, mockup={mockup_video.filename}")
        
        # Créer des noms de fichiers uniques
        timestamp = int(time.time())
        main_path = f"{UPLOAD_FOLDER}/main_{timestamp}.mp4"
        mockup_path = f"{UPLOAD_FOLDER}/mockup_{timestamp}.mp4"
        output_path = f"{OUTPUT_FOLDER}/output_{timestamp}.mp4"
        
        # Vérifier si les dossiers existent
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Enregistrer les fichiers
        try:
            main_video.save(main_path)
            mockup_video.save(mockup_path)
            logger.info("Fichiers sauvegardés avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des fichiers: {str(e)}")
            return jsonify({'error': 'Erreur lors de la sauvegarde des fichiers'}), 500
        
        # Traiter les vidéos avec ffmpeg
        try:
            command = [
                '/bin/bash', 
                '/app/process_video.sh', 
                main_path, 
                mockup_path,
                output_path
            ]
            
            logger.info(f"Exécution de la commande: {' '.join(command)}")
            
            # Augmenter le timeout à 600 secondes (10 minutes)
            process = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=600
            )
            
            if process.returncode != 0:
                logger.error(f"Erreur ffmpeg: {process.stderr}")
                return jsonify({
                    'error': 'Erreur lors du traitement ffmpeg',
                    'details': process.stderr
                }), 500
            
            logger.info("Traitement ffmpeg terminé avec succès")
            
            # Vérifier si le fichier de sortie existe
            if not os.path.exists(output_path):
                logger.error("Le fichier de sortie n'a pas été créé")
                return jsonify({'error': 'Le fichier de sortie est manquant'}), 500
            
            # Renvoyer l'URL de la vidéo traitée
            video_name = os.path.basename(output_path)
            result_url = f"{request.host_url}videos/{video_name}"
            
            logger.info(f"URL de résultat générée: {result_url}")
            
            return jsonify({
                'success': True,
                'video_url': result_url,
                'message': 'Vidéo traitée avec succès'
            })
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout lors du traitement de la vidéo")
            return jsonify({'error': 'Le traitement de la vidéo a pris trop de temps'}), 504
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement: {str(e)}")
            return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500
        finally:
            # Nettoyage des fichiers temporaires
            try:
                if os.path.exists(main_path):
                    os.remove(main_path)
                if os.path.exists(mockup_path):
                    os.remove(mockup_path)
                logger.info("Nettoyage des fichiers temporaires effectué")
            except Exception as e:
                logger.warning(f"Erreur lors du nettoyage des fichiers: {str(e)}")

    except Exception as e:
        logger.error(f"Erreur générale: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    try:
        file_path = f"{OUTPUT_FOLDER}/{filename}"
        if not os.path.exists(file_path):
            logger.error(f"Fichier non trouvé: {file_path}")
            return jsonify({'error': 'Fichier non trouvé'}), 404
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du fichier: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'envoi du fichier: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
