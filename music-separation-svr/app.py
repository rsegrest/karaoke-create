import sys
import os
import argparse
import torch
import torchaudio
import traceback
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

# Add separate_music to path to import separation.py
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'separate_music'))

# Import AudioSeparation from separation.py
try:
    from separation import AudioSeparation
except ImportError as e:
    print(f"Error importing AudioSeparation: {e}")
    sys.exit(1)

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

# Global separator instance
separator = None

def get_separator():
    global separator
    if separator is None:
        try:
            print(f"Initializing AudioSeparation...")
            separator = AudioSeparation()
            print("Separator initialized successfully.")
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
    
    input_path = Path(data['input_path'])
    if not input_path.exists():
         return jsonify({'error': f'Input file not found: {input_path}'}), 404

    # Output directory shared_data/outputs/<filename_no_ext>
    base_filename = input_path.stem
    output_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "shared_data" / "outputs" / base_filename
    output_dir.mkdir(parents=True, exist_ok=True)

    separator = get_separator()
    if not separator:
        return jsonify({'error': 'AudioSeparation not initialized'}), 500

    print(f"Processing: {input_path}")
    
    try:
        # separate() takes audio_path and output_dir_name (relative to "output" in original script)
        # But we want to control exact output dir.
        # separation.py's separate method does: output_dir = os.path.join("output", output_dir)
        # We need to change how we call it or modify separation.py to accept absolute path.
        # For now, let's look at separation.py again.
        # It does:
        # output_dir = os.path.join("output", output_dir)
        # os.makedirs(output_dir, exist_ok=True)
        # This forces output to be in a subdirectory "output".
        # We can temporarily chdir or modify the class. 
        # Modifying the class (monkey patch) or just the file is better.
        
        # Actually, let's just instantiate the separator and run the logic ourselves if the method is too restrictive,
        # OR we can just pass the relative path if we run from the right CWD.
        # Let's try to monkey patch separate_sources or just call separate with a path that works out.
        
        # simpler: Let's just modify separation.py to allow absolute paths if provided.
        # But wait, I shouldn't modify existing code unless necessary.
        
        # Let's try to just use the class and call separate. 
        # If I pass output_dir="foo", it goes to "output/foo".
        # If I want it in shared_data/outputs/foo, I can't easily do it with current separation.py
        
        # Let's import the class and use its internal model directly, or just copy the logic.
        # The logic is simple enough: load, resample, separate_sources, save.
        # I'll re-implement the glue logic here to have full control over paths.
        
        # ... actually, separation.py is small. I can just copy the relevant parts into my service 
        # OR I can update separation.py to be more flexible (better for codebase hygiene).
        # Let's try to usage the existing class but be clever about CWD or just accept it goes to "output/" 
        # and move it later.
        
        # Let's move the files after generation.
        # music-separation-svr CWD is probably the root or where I run it from.
        # If I run from project root, "output" will be created there.
        # I can then move "output/<name>/..." to "shared_data/outputs/<name>".
        
        # Let's try to just run it and see where it goes, then move.
        # separate(audio_path, output_dir_name) -> output/output_dir_name/
        
        target_output_subdir = base_filename
        separator.separate(str(input_path), target_output_subdir)
        
        # Expected locations:
        # output/<target_output_subdir>/vocals.wav
        # output/<target_output_subdir>/instrumental.wav
        
        # Move to shared_data/outputs/<base_filename>
        # ensure output_dir exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        src_dir = Path("output") / target_output_subdir
        if src_dir.exists():
            import shutil
            for file_name in ["vocals.wav", "instrumental.wav"]:
                src = src_dir / file_name
                dst = output_dir / file_name
                if src.exists():
                    shutil.move(str(src), str(dst))
            
            # Cleanup source dir
            # shutil.rmtree(src_dir) # Maybe keep for debugging? No, clean up.
            try:
                shutil.rmtree(src_dir)
            except:
                pass
            
            # Cleanup "output" dir if empty?
            # try:
            #     os.rmdir("output")
            # except:
            #     pass

        results = {
            'accompaniment_file': str(output_dir / "instrumental.wav"),
            'vocal_file': str(output_dir / "vocals.wav")
        }
        return jsonify(results), 200

    except Exception as e:
        print(f"Exception during separation: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def main():
    # Pre-initialize handler if possible
    get_separator()
    app.run(debug=True, port=5002)

if __name__ == "__main__":
    main()
