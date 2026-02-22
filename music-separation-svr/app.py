import sys
import os
import traceback
from pathlib import Path
from flask import Flask, request, jsonify
from separation import AudioSeparation

app = Flask(__name__)

# Add local FFMPEG bin to PATH
ffmpeg_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs", "ffmpeg_bin")
if os.path.exists(ffmpeg_bin):
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
    # Also add for DLL search path on Python 3.8+
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(ffmpeg_bin)
        except Exception:
            pass

# Set stdout encoding to utf-8
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

# Global handler instance
separator = None

def get_separator():
    global separator
    if separator is None:
        try:
            print("Initializing HDEMUCS Separation Model...")
            separator = AudioSeparation()
            print("Service initialized successfully.")
        except Exception as e:
            print(f"Exception during initialization: {e}")
            traceback.print_exc()
            separator = None
    return separator

@app.route('/separate', methods=['POST'])
def separate_audio_endpoint():
    data = request.get_json()
    if not data or 'input_path' not in data:
        return jsonify({'error': 'Missing input_path'}), 400
    if 'output_dir' not in data:
        return jsonify({'error': 'Missing output_dir'}), 400
    
    input_path = Path(data['input_path'])
    if not input_path.exists():
         return jsonify({'error': f'Input file not found: {input_path}'}), 404

    base_filename = input_path.stem
    output_dir = Path(data['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    sep = get_separator()
    if not sep:
        return jsonify({'error': 'Separation model not initialized'}), 500

    print(f"Processing: {input_path}")
    results = {}

    try:
        # Pass the output_dir directly.
        sep.separate(str(input_path), str(output_dir))
        
        # AudioSeparation saves directly to the passed output_dir now.
        vocals_dst = output_dir / "vocals.wav"
        inst_dst = output_dir / "instrumental.wav"
            
        results['vocal_file'] = str(vocals_dst) if vocals_dst.exists() else None
        results['accompaniment_file'] = str(inst_dst) if inst_dst.exists() else None
        
        return jsonify(results), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def main():
    # Pre-initialize handler if possible
    get_separator()
    app.run(debug=False, port=5002, use_reloader=False)

if __name__ == "__main__":
    main()
