import os
import time
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

UPLOAD_FOLDER = '/app/uploads'
OUTPUT_FOLDER = '/app/output'

@app.route('/process-video', methods=['POST'])
def process_video():
    # Vérifier les fichiers
    if 'main_video' not in request.files or 'mockup_video' not in request.files:
        return jsonify({'error': 'Les deux fichiers vidéo sont requis'}), 400
    
    # Récupérer les fichiers
    main_video = request.files['main_video']
    mockup_video = request.files['mockup_video']
    
    # Créer des noms de fichiers uniques
    timestamp = int(time.time())
    main_path = f"{UPLOAD_FOLDER}/main_{timestamp}.mp4"
    mockup_path = f"{UPLOAD_FOLDER}/mockup_{timestamp}.mp4"
    output_path = f"{OUTPUT_FOLDER}/output_{timestamp}.mp4"
    
    # Enregistrer les fichiers
    main_video.save(main_path)
    mockup_video.save(mockup_path)
    
    # Traiter les vidéos avec ffmpeg
    try:
        command = [
            '/bin/bash', 
            '/app/process_video.sh', 
            main_path, 
            mockup_path,
            output_path
        ]
        
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            return jsonify({
                'error': 'Erreur lors du traitement ffmpeg',
                'details': process.stderr
            }), 500
        
        # Renvoyer l'URL de la vidéo traitée
        video_name = os.path.basename(output_path)
        result_url = f"{request.host_url}videos/{video_name}"
        
        return jsonify({
            'success': True,
            'video_url': result_url,
            'message': 'Vidéo traitée avec succès'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500

@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    return send_file(f"{OUTPUT_FOLDER}/{filename}")

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)