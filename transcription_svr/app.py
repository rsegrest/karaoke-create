from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError
from pathlib import Path
import traceback
from transcribe import transcribe_to_structured_data
import argparse

app = Flask(__name__)
CORS(app)

# class QueueRequestSchema(Schema):
#     song_title = fields.Str(required=True)
#     original_artist = fields.Str(required=True)
#     performer_name = fields.Str(required=True)
#     # music_file is handled separately via request.files

# @app.route("/")
# def usage():
#     return """
#     <p>Queueing Proxy Server API</p><p>Use the /queue-request endpoint to queue a request.</p><p>Example: <a href="/queue-request">/queue-request</a></p>
#     """

import requests
import os

@app.route('/transcribe', methods=['POST'])
def transcribe_audio_endpoint():
    # try:
    #     # Validate request form data against schema
    #     result = schema.load(request.form)
    # except ValidationError as err:
    #     return jsonify(err.messages), 400
    # if not data or 'input_path' not in data:
    #     return jsonify({'error': 'Missing input_path'}), 400
    
    # Validate file presence
    if 'music_file' not in request.files:
        return jsonify({'music_file': ['Missing data for required field.']}), 400
    
    file = request.files['music_file']
    if file.filename == '':
        return jsonify({'music_file': ['No selected file.']}), 400

    # Validate file presence
    if 'music_file' not in request.files:
        return jsonify({'music_file': ['Missing data for required field.']}), 400
    
    file = request.files['music_file']
    if file.filename == '':
        return jsonify({'music_file': ['No selected file.']}), 400
    
    if file: #and allowed_file(file.filename):
        filename = file.filename # secure_filename(file.filename)
        os.makedirs('uploads', exist_ok=True) # Ensure uploads directory exists
        file.save(os.path.join('uploads', filename))
        input_path = os.path.join('uploads', filename)
    else:
        return jsonify({'music_file': ['Invalid file type.']}), 400

    # Output directory shared_data/outputs/<filename_no_ext>
    # base_filename = input_path.stem
    output_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "shared_data" / "outputs" / filename
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        
        target_output_subdir = filename
        # Pass the file path (string), not the file object
        json_file, csv_file, lyrics_txt = transcribe_to_structured_data(input_path, target_output_subdir)
        
        print("result:")
        print(json_file)
        print(csv_file)
        print(lyrics_txt)

        # Expected locations:
        # output/<target_output_subdir>/vocals.wav
        # output/<target_output_subdir>/instrumental.wav
        
        # Move to shared_data/outputs/<base_filename>
        # ensure output_dir exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        src_dir = Path("output") / target_output_subdir

        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            lyrics_json_data = json.load(f)

        results = {
            'lyrics_txt': lyrics_txt,
            'lyrics_json': lyrics_json_data,
        }
        return jsonify(results), 200

    except Exception as e:
        print(f"Exception during lyrics extraction: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def main():
    # Pre-initialize handler if possible
    # get_separator()
    app.run(debug=False, port=5003, use_reloader=False)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Transcribe vocals to text.")
    # parser.add_argument("--input", required=True, help="Input audio file path")
    # parser.add_argument("--output", required=True, help="Output directory for lyrics")
    # args = parser.parse_args()

    # transcribe_audio_endpoint(args.input, args.output)
    main()