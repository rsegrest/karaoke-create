from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
CORS(app)

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
    
    # Use a secure filename or just the provided one for now (assuming internal use)
    # Ideally should use secure_filename
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    save_path = os.path.join(shared_uploads_dir, filename)
    file.save(save_path)

    # Call Music Separation Service
    separation_service_url = "http://localhost:5002/separate"
    try:
        print(f"Calling separation service for {save_path}...")
        response = requests.post(separation_service_url, json={'input_path': save_path})
        if response.status_code == 200:
            separation_results = response.json()
            accompanyment_file = separation_results.get('accompaniment_file', 'Error generating accompaniment')
            vocal_file = separation_results.get('vocal_file', 'Error generating vocals')
        else:
            print(f"Separation service failed: {response.text}")
            accompanyment_file = f"Error: Separation service returned {response.status_code}"
            vocal_file = f"Error: Separation service returned {response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to separation service: {e}")
        accompanyment_file = "Error: Could not connect to separation service"
        vocal_file = "Error: Could not connect to separation service"

    
    # Call Transcription Service
    transcription_service_url = "http://localhost:5003/transcribe"
    file.seek(0) # Reset file pointer to beginning before sending again
    files={ 'music_file': file}
    try:
        print(f"Calling transcription service...")
        # Post music file to transcription service
        response = requests.post(transcription_service_url, files=files)
        # response = requests.post(transcription_service_url, json={'music_file': file})
        if response.status_code == 200:
            transcription_results = response.json()
            lyrics_txt = transcription_results.get('lyrics_txt', 'Error generating lyrics')
            lyrics_json = transcription_results.get('lyrics_json', 'Error generating lyrics JSON')
        else:
            print(f"Transcription service failed: {response.text}")
            lyrics_txt = f"Error: Transcription service returned {response.status_code}"
            lyrics_json = f"Error: Transcription service returned {response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to transcription service: {e}")
        lyrics_txt = "Error: Could not connect to transcription service"
        lyrics_json = "Error: Could not connect to transcription service"

    # If validation succeeds, result contains the validated data
    song_title = result['song_title']
    original_artist = result['original_artist']
    performer_name = result['performer_name']
    music_file = filename
    
    # Placeholder values for now, as logic to generate these is missing
    original_music_file = music_file

    return jsonify({
        'song_title': song_title,
        'original_artist': original_artist,
        'performer_name': performer_name,
        'lyrics_txt': lyrics_txt,
        'lyrics_json': lyrics_json,
        'original_music_file': original_music_file,
        'accompanyment_file': accompanyment_file,
        'vocal_file': vocal_file,
    }), 200

def main():
    app.run(debug=True, port=5001)

if __name__ == "__main__":
    main()
