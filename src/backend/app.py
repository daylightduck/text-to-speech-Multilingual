from flask import Flask, request, jsonify, send_file, send_from_directory, url_for
from flask_cors import CORS
from tts_service import TTSService, VOICE_CONFIG, is_cuda_available
import os
from pathlib import Path

# Get the absolute path to the frontend directory
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'

print(f"Frontend directory: {FRONTEND_DIR}")
print(f"Frontend directory exists: {FRONTEND_DIR.exists()}")
print(f"Frontend directory contents: {list(FRONTEND_DIR.glob('*'))}")

app = Flask(__name__, 
            static_folder=str(FRONTEND_DIR),
            static_url_path='')
CORS(app)

tts_service = TTSService()

@app.route('/')
def serve_frontend():
    print(f"Serving frontend from: {app.static_folder}")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/styles.css')
def serve_css():
    return send_from_directory(app.static_folder, 'styles.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory(app.static_folder, 'script.js')

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    audio_dir = Path(__file__).parent / 'static' / 'audio'
    return send_from_directory(str(audio_dir), filename)

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Return available voices"""
    voices = []
    # Group voices by language
    language_groups = {}
    
    for voice_id, config in VOICE_CONFIG.items():
        language = config['language']
        if language not in language_groups:
            language_groups[language] = []
            
        language_groups[language].append({
            'id': voice_id,
            'name': config['name'],
            'emoji': config['emoji'],
            'language': language
        })
    
    # Convert to list format for the frontend
    for language, voice_list in language_groups.items():
        voices.append({
            'language': language,
            'voices': voice_list
        })
        
    return jsonify(voices)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Return available devices (CPU/GPU)"""
    devices = [
        {
            'id': 'cpu',
            'name': 'CPU',
            'emoji': '💻',
            'description': 'Central Processing Unit (slower but always available)'
        }
    ]
    
    # Add GPU if available
    if is_cuda_available():
        devices.append({
            'id': 'cuda',
            'name': 'GPU',
            'emoji': '🖥️',
            'description': 'Graphics Processing Unit (faster processing)'
        })
        
    return jsonify(devices)

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'af_nicole')
    device = data.get('device', 'cpu')  # Default to CPU if not specified
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        audio_file, original_text, voice_id, emoji, voice_name, language, used_device = tts_service.generate_speech(
            text, voice, device
        )
        # Get just the filename without the full path
        filename = os.path.basename(audio_file)
        print(f"Generated audio file: {audio_file}")
        print(f"Filename: {filename}")
        return jsonify({
            'success': True,
            'audio_file': f'/audio/{filename}',
            'text': original_text,
            'voice': voice_id,
            'voice_name': voice_name,
            'emoji': emoji,
            'language': language,
            'device': used_device
        })
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 