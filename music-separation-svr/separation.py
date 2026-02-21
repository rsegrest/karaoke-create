"""Credit: https://pytorch.org/audio/stable/tutorials/hybrid_demucs_tutorial.html"""

import torch
import torchaudio
from torchaudio.transforms import Fade, Resample
import sys
import subprocess
import shutil
import os
import torch
import argparse

# Add local FFMPEG bin to PATH
ffmpeg_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs", "ffmpeg_bin")
if os.path.exists(ffmpeg_bin):
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(ffmpeg_bin)
        except Exception:
            pass

class AudioSeparation:
    def __init__(self, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Demucs Separation Backend Initialized. Target Device: {self.device}")

    def separate(self, audio_path, output_dir_name):
        print(f"Starting Demucs high-fidelity separation on {audio_path}...")
        
        # We will dispatch demucs out to a subprocess to prevent threading deadlocks in the Flask reactor
        # The demucs CLI safely handles threading, model downloading, and audio formatting automatically.
        python_exe = sys.executable
        
        # Create a temporary output location for demucs to work
        temp_out = os.path.join("output", "temp_demucs")
        os.makedirs(temp_out, exist_ok=True)
        
        # Command: python -m demucs.separate -n htdemucs --two-stems vocals -d cpu -o <temp_out> <audio_path>
        command = [
            python_exe,
            "-m", "demucs.separate",
            "-n", "htdemucs",
            "--two-stems", "vocals",
            "-d", self.device,
            "-o", temp_out,
            audio_path
        ]
        
        print("Executing:", " ".join(command))
        try:
            # We enforce a timeout or check=True to block until separated
            subprocess.run(command, check=True)
            print("Demucs processing completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Demucs processing failed with error: {e}")
            return
            
        # Demucs creates an output folder structure like: <output>/htdemucs/<track_name>/
        # Extract the track name without extension
        track_name = os.path.splitext(os.path.basename(audio_path))[0]
        demucs_result_dir = os.path.join(temp_out, "htdemucs", track_name)
        
        if not os.path.exists(demucs_result_dir):
            print(f"Error: Expected demucs output directory not found at {demucs_result_dir}")
            return

        # Prepare final output directory
        final_out_dir = os.path.join("output", output_dir_name)
        os.makedirs(final_out_dir, exist_ok=True)

        # Move vocals.wav and no_vocals.wav to the target directory
        try:
            src_vocals = os.path.join(demucs_result_dir, "vocals.wav")
            src_no_vocals = os.path.join(demucs_result_dir, "no_vocals.wav")
            
            dst_vocals = os.path.join(final_out_dir, "vocals.wav")
            dst_no_vocals = os.path.join(final_out_dir, "instrumental.wav") # Renamed for our API
            
            if os.path.exists(src_vocals):
                shutil.move(src_vocals, dst_vocals)
                print(f"Saved Vocals to {dst_vocals}")
            if os.path.exists(src_no_vocals):
                shutil.move(src_no_vocals, dst_no_vocals)
                print(f"Saved Instrumental to {dst_no_vocals}")
                
            # Cleanup temp demucs output
            shutil.rmtree(temp_out, ignore_errors=True)
            print(f"Separation complete. Output saved to {final_out_dir}")
            
        except Exception as e:
            print(f"Error moving separated files: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Separate audio into Vocals and Instrumental tracks.")
    parser.add_argument("--input", required=True, help="Input audio file path")
    parser.add_argument("--output", required=True, help="Output directory for separated tracks")
    args = parser.parse_args()

    separator = AudioSeparation()
    separator.separate(args.input, args.output)