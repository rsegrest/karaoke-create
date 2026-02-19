from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError
from pathlib import Path
import traceback
from transcribe import transcribe_to_structured_data

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
        # if src_dir.exists():
            # import shutil
            # for file_name in ["vocals.wav", "instrumental.wav"]:
            #     src = src_dir / file_name
            #     dst = output_dir / file_name
            #     if src.exists():
            #         shutil.move(str(src), str(dst))
            
            # Cleanup source dir
            # shutil.rmtree(src_dir) # Maybe keep for debugging? No, clean up.
            # try:
            #     shutil.rmtree(src_dir)
            # except:
            #     pass
            
            # Cleanup "output" dir if empty?
            # try:
            #     os.rmdir("output")
            # except:
            #     pass

        results = {
            'lyrics_txt': lyrics_txt,
            'lyrics_json': json_file,
            # 'accompaniment_file': str(output_dir / "instrumental.wav"),
            # 'vocal_file': str(output_dir / "vocals.wav")
        }
        return jsonify(results), 200

    except Exception as e:
        print(f"Exception during lyrics extraction: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def main():
    # Pre-initialize handler if possible
    # get_separator()
    app.run(debug=True, port=5003)

if __name__ == "__main__":
    main()
