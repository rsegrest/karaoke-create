from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError
from models import db, Song
from output_manager import OutputManager

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///karaoke.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Initialize Output Manager
output_manager = OutputManager()

class QueueRequestSchema(Schema):
    song_title = fields.Str(required=True)
    original_artist = fields.Str(required=True)
    performer_name = fields.Str(required=True)
    # music_file is handled separately via request.files

@app.route("/")
def usage():
    return """
    <p>Queueing Proxy Server API</p><p>Use the /queue-request endpoint to queue a request.</p><p>Example: <a href="/queue-request">/queue-request</a></p>
    """

import requests
import os
import threading

def process_song_async(app_context, song_id, save_path, filename, mimetype):
    with app_context:
        # Call Music Separation Service
        separation_service_url = "http://localhost:5002/separate"
        accompanyment_file = None
        vocal_file = None
        
        output_manager.update_song_status(song_id, 'separating')
        
        try:
            print(f"Calling separation service for {save_path}...")
            response = requests.post(separation_service_url, json={'input_path': save_path})
            if response.status_code == 200:
                separation_results = response.json()
                accompanyment_file = separation_results.get('accompaniment_file')
                vocal_file = separation_results.get('vocal_file')
                
                output_manager.update_song_status(
                    song_id,
                    'transcribing',
                    instrumental_file_path=accompanyment_file,
                    vocals_file_path=vocal_file
                )
                output_manager.update_instrumental_file_path(song_id, accompanyment_file)
                output_manager.update_vocal_file_path(song_id, vocal_file)
            else:
                print(f"Separation service failed: {response.text}")
                output_manager.update_song_status(song_id, 'error_separation')
                return
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to separation service: {e}")
            output_manager.update_song_status(song_id, 'error_separation_connection')
            return
        
        # Call Transcription Service
        transcription_service_url = "http://localhost:5003/transcribe"
        lyrics_txt = None
        lyrics_json = None
        
        try:
            print(f"Calling transcription service...")
            with open(save_path, 'rb') as f:
                files={'music_file': (filename, f, mimetype)}
                response = requests.post(transcription_service_url, files=files)
            if response.status_code == 200:
                transcription_results = response.json()
                lyrics_txt = transcription_results.get('lyrics_txt')
                lyrics_json = transcription_results.get('lyrics_json')
                
                output_manager.update_song_status(
                    song_id, 
                    'done', 
                    lyrics_text=lyrics_txt,
                    lyrics_json=lyrics_json
                )
                output_manager.update_lyrics_text(song_id, lyrics_txt)
                output_manager.update_lyrics_json(song_id, lyrics_json)
            else:
                print(f"Transcription service failed: {response.text}")
                output_manager.update_song_status(song_id, 'error_transcription')
                return
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to transcription service: {e}")
            output_manager.update_song_status(song_id, 'error_transcription_connection')
            return

@app.route('/queue_request', methods=['POST'])
def queue_request():
    schema = QueueRequestSchema()
    try:
        # Validate request form data against schema
        result = schema.load(request.form)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Validate file presence
    if 'music_file' not in request.files:
        return jsonify({'music_file': ['Missing data for required field.']}), 400
    
    file = request.files['music_file']
    if file.filename == '':
        return jsonify({'music_file': ['No selected file.']}), 400

    # Save file to shared uploads directory
    shared_uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared_data', 'uploads')
    os.makedirs(shared_uploads_dir, exist_ok=True)
    
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    save_path = os.path.join(shared_uploads_dir, filename)
    file.save(save_path)

    # Convert to WAV for ML model compatibility (avoid soundfile errors on .m4a)
    import subprocess
    wav_path = os.path.join(shared_uploads_dir, os.path.splitext(filename)[0] + ".wav")
    if not filename.lower().endswith('.wav'):
        print(f"Converting {filename} to .wav for ML compatibility...")
        try:
            subprocess.run(["ffmpeg", "-y", "-i", save_path, wav_path], check=True, capture_output=True)
            save_path = wav_path
            filename = os.path.basename(wav_path)
            print("Conversion successful.")
        except Exception as e:
            print(f"FFMPEG conversion failed: {e}")

    # Create DB Entry
    song_title = result['song_title']
    original_artist = result['original_artist']
    performer_name = result['performer_name']
    
    new_song = output_manager.add_song_data(
        title=song_title,
        artist=original_artist,
        original_file_path=save_path
    )
    song_id = new_song.id
    print(f"Created song entry ID: {song_id}")

    # Start ML processing in a background thread so we don't block the UI
    thread = threading.Thread(
        target=process_song_async, 
        args=(app.app_context(), song_id, save_path, filename, file.mimetype)
    )
    thread.daemon = True
    thread.start()

    # Return response immediately
    return jsonify({
        'song_id': song_id,
        'song_title': song_title,
        'original_artist': original_artist,
        'performer_name': performer_name,
        'original_music_file': filename,
        'status': 'queued'
    }), 201

@app.route('/list_available_songs')
def list_available_songs():
    songs = output_manager.get_all_song_data()
    return jsonify([{'song_id': song.id, 'song_title': song.title, 'original_artist': song.artist, 'status': song.status, 'owner_id': song.owner_id} for song in songs])

@app.route('/get_song_data')
def get_song_data():
    song_id = request.args.get('song_id')
    song = output_manager.get_song_data(song_id)
    return jsonify({'song_id': song.id, 'song_title': song.title, 'original_artist': song.artist, 'status': song.status, 'owner_id': getattr(song, 'owner_id', None), 'lyrics_json': song.lyrics_json, 'lyrics_text': song.lyrics_text})

@app.route('/stream_audio')
def stream_audio():
    song_id = request.args.get('song_id')
    audio_type = request.args.get('type') # 'instrumental', 'vocals', 'original'
    song = output_manager.get_song_data(song_id)
    if not song:
        return jsonify({'error': 'Song not found'}), 404
        
    path = None
    if audio_type == 'instrumental':
        path = song.instrumental_file_path
    elif audio_type == 'vocals':
        path = song.vocals_file_path
    elif audio_type == 'original':
        path = song.original_file_path
        
    if path and os.path.exists(path):
        return send_file(path)
    return jsonify({'error': 'File not found on disk'}), 404

@app.route('/remove_song_data')
def remove_song_data():
    song_id = request.args.get('song_id')
    output_manager.remove_song_data(song_id)
    return jsonify({'song_id': song_id, 'status': 'removed'})

@app.route('/find_song_by_title')
def find_song_by_title():
    song_title = request.args.get('song_title')
    songs = output_manager.find_song_by_title(song_title)
    return jsonify([{'song_id': song.id, 'song_title': song.title, 'original_artist': song.artist, 'status': song.status, 'owner_id': song.owner_id} for song in songs])

@app.route('/find_songs_by_original_artist')
def find_songs_by_original_artist():
    original_artist = request.args.get('original_artist')
    songs = output_manager.find_songs_by_original_artist(original_artist)
    return jsonify([{'song_id': song.id, 'song_title': song.title, 'original_artist': song.artist, 'status': song.status, 'owner_id': song.owner_id} for song in songs])

def main():
    app.run(debug=False, port=5001, use_reloader=False)

if __name__ == "__main__":
    main()
