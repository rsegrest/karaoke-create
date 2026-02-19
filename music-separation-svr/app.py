import sys
import os
import argparse
import torch
import torchaudio
import traceback
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

# Add the temp_ace_step directory to sys.path
# Assuming separate_music/temp_ace_step exists and we can reuse it, or we need to copy it.
# For now, let's assume we can reference the one in separate_music if it's there, 
# or we should probably have it in a common lib. 
# Let's try to add the path relative to this new service.
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'separate_music', 'temp_ace_step'))

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

try:
    if hasattr(torchaudio, "set_audio_backend"):
        torchaudio.set_audio_backend("soundfile")
        print("Set torchaudio backend to soundfile")
except Exception as e:
    print(f"Failed to set backend: {e}")

# Global handler instance
handler = None

def get_handler():
    global handler
    if handler is None:
        try:
            from acestep.handler import AceStepHandler
            print(f"Initializing ACE-STEP Handler (v1.5)...")
            handler = AceStepHandler()
            
            # Setup paths for initialization
            # Reusing the model path from separate_music for now
            project_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "separate_music", "temp_ace_step")
            config_path = "acestep-v15-turbo"
            
            # Initialize service
            status, success = handler.initialize_service(
                project_root=project_root,
                config_path=config_path,
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
            
            if not success:
                print(f"Failed to initialize service: {status}")
                handler = None
            else:
                print("Service initialized successfully.")
                
        except ImportError as e:
            print(f"Error importing AceStepHandler: {e}")
            handler = None
        except Exception as e:
            print(f"Exception during initialization: {e}")
            traceback.print_exc()
            handler = None
    return handler

@app.route('/separate', methods=['POST'])
def separate_audio_endpoint():
    data = request.get_json()
    if not data or 'input_path' not in data:
        return jsonify({'error': 'Missing input_path'}), 400
    
    input_path = Path(data['input_path'])
    if not input_path.exists():
         return jsonify({'error': f'Input file not found: {input_path}'}), 404

    # Output directory relative to shared data or specified?
    # Let's say we put outputs in shared_data/outputs/<filename_no_ext>
    base_filename = input_path.stem
    output_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "shared_data" / "outputs" / base_filename
    output_dir.mkdir(parents=True, exist_ok=True)

    handler = get_handler()
    if not handler:
        return jsonify({'error': 'ACE-STEP handler not initialized'}), 500

    print(f"Processing: {input_path}")
    results = {}

    def generate_and_save(prompt, filename):
        print(f"Generating {filename} with prompt: '{prompt}'...")
        try:
            # Using 'repaint' task for separation/editing
            result = handler.generate_music(
                captions=prompt,
                src_audio=str(input_path),
                task_type="repaint",
                lyrics="",
                inference_steps=50,
                guidance_scale=7.0,
                audio_duration=0, # Auto-detect from source
            )
            
            if result.get('success'):
                audios = result.get('audios', [])
                if audios:
                    # Save the first audio result
                    audio_data = audios[0]
                    tensor = audio_data['tensor']
                    sample_rate = audio_data['sample_rate']
                    
                    save_path = output_dir / filename
                    
                    # Ensure tensor is 2D [channels, samples]
                    if tensor.dim() == 1:
                        tensor = tensor.unsqueeze(0)
                        
                    # Save with soundfile
                    import soundfile as sf
                    audio_np = tensor.transpose(0, 1).numpy()
                    sf.write(str(save_path), audio_np, sample_rate)
                    print(f"Saved to: {save_path}")
                    return str(save_path)
                else:
                    print("No audio generated.")
                    return None
            else:
                print(f"Generation failed: {result.get('error')}")
                return None
                
        except Exception:
            traceback.print_exc()
            return None

    # Generate Instrumental (Remove Vocals)
    print("Generating Instrumental Track...")
    inst_path = generate_and_save("instrumental, backing track, no vocals", "accompaniment.wav")
    results['accompaniment_file'] = inst_path

    # Generate Vocals (Remove Instruments)
    print("Generating Vocals Track...")
    voc_path = generate_and_save("vocals only, a cappella, no instruments", "vocals.wav")
    results['vocal_file'] = voc_path

    return jsonify(results), 200

def main():
    # Pre-initialize handler if possible
    get_handler()
    app.run(debug=True, port=5002)

if __name__ == "__main__":
    main()
