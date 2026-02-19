"""Credit: https://pytorch.org/audio/stable/tutorials/hybrid_demucs_tutorial.html"""

import torch
import torchaudio
from torchaudio.transforms import Fade, Resample
from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS
import soundfile as sf
import argparse
import os
import subprocess
import tempfile
import sys

# Add local FFMPEG bin to PATH
ffmpeg_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs", "ffmpeg_bin")
if os.path.exists(ffmpeg_bin):
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(ffmpeg_bin)
        except Exception:
            pass

def convert_audio_to_wav(input_path):
    """Converts audio to a temporary WAV file using FFMPEG."""
    try:
        temp_dir = tempfile.gettempdir()
        temp_wav = os.path.join(temp_dir, f"temp_{os.path.basename(input_path)}.wav")
        
        command = [
            "ffmpeg", "-y", "-i", input_path, 
            "-ac", "2", "-ar", "44100", # Force stereo 44.1k for compatibility
            temp_wav
        ]
        
        print(f"Converting {input_path} to WAV...")
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return temp_wav
    except subprocess.CalledProcessError as e:
        print(f"FFMPEG conversion failed: {e}")
        return None
    except FileNotFoundError:
        print("FFMPEG not found. Please ensure FFMPEG is installed and in PATH.")
        return None

def ensure_stereo(waveform):
    if waveform.shape[0] == 1:
        return torch.cat([waveform, waveform], dim=0)
    return waveform

class AudioSeparation:
    def __init__(self, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        self.bundle = HDEMUCS_HIGH_MUSDB_PLUS
        self.model = self.bundle.get_model().to(self.device)
        self.sample_rate = self.bundle.sample_rate

    def separate(self, audio_path, output_dir):
        print(f"Loading audio from {audio_path}...")
        
        temp_wav = None
        load_path = audio_path
        
        # Check if we need to convert (if not .wav or if loading fails)
        if not audio_path.lower().endswith(".wav"):
            temp_wav = convert_audio_to_wav(audio_path)
            if temp_wav:
                load_path = temp_wav
            else:
                print("Failed to convert audio, attempting to load directly...")

        try:
            audio_np, sr = sf.read(load_path, dtype="float32")
            if audio_np.ndim == 1:
                waveform = torch.from_numpy(audio_np).unsqueeze(0)
            else:
                waveform = torch.from_numpy(audio_np.T)
        except Exception as e:
            print(f"Error loading audio: {e}")
            if temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)
            return

        # Cleanup temp file if created
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

        waveform = waveform.to(self.device)
        waveform = ensure_stereo(waveform)

        # Resample to model's expected sample rate
        if sr != self.sample_rate:
            print(f"Resampling from {sr}Hz to {self.sample_rate}Hz...")
            resample = Resample(sr, self.sample_rate).to(self.device)
            waveform = resample(waveform)

        ref = waveform.mean(0)
        waveform = (waveform - ref.mean()) / ref.std()  # Normalize

        print("Separating sources...")
        sources = self.separate_sources(
            self.model,
            waveform[None],
            self.sample_rate,
            device=self.device
        )[0]

        sources = sources * ref.std() + ref.mean()
        sources_list = self.model.sources
        source_dict = dict(zip(sources_list, sources))
        output_dir = os.path.join("output", output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Save Vocals
        print("Saving Vocals...")
        vocals = source_dict["vocals"].cpu().detach()
        sf.write(os.path.join(output_dir, "vocals.wav"), vocals.T.numpy(), self.sample_rate)
        
        # Mix and Save Instrumental (Bass + Drums + Other)
        print("Saving Instrumental...")
        instrumental = source_dict["bass"] + source_dict["drums"] + source_dict["other"]
        instrumental = instrumental.cpu().detach()
        sf.write(os.path.join(output_dir, "instrumental.wav"), instrumental.T.numpy(), self.sample_rate)

        print(f"Separation complete. Output saved to {output_dir}")

    def separate_sources(
        self,
        model: torch.nn.Module,
        mix: torch.Tensor,
        sample_rate: int,
        segment: float = 10.0,
        overlap: float = 0.1,
        device: torch.device = None,
        chunk_fade_shape: str = "linear",
    ) -> torch.Tensor:
        """
        From: https://pytorch.org/audio/stable/tutorials/hybrid_demucs_tutorial.html

        Apply model to a given mixture. Use fade, and add segments together in order to add model segment by segment.

        Args:
            segment (int): segment length in seconds
            device (torch.device, str, or None): if provided, device on which to
                execute the computation, otherwise `mix.device` is assumed.
                When `device` is different from `mix.device`, only local computations will
                be on `device`, while the entire tracks will be stored on `mix.device`.
        """
        if device is None:
            device = mix.device
        else:
            device = torch.device(device)

        batch, channels, length = mix.shape

        chunk_len = int(sample_rate * segment * (1 + overlap))
        start = 0
        end = chunk_len
        overlap_frames = overlap * sample_rate
        fade = Fade(
            fade_in_len=0, fade_out_len=int(overlap_frames), fade_shape=chunk_fade_shape
        ).to(device)

        final = torch.zeros(batch, len(model.sources), channels, length, device=device)

        while start < length - overlap_frames:
            chunk = mix[:, :, start:end]
            with torch.no_grad():
                out = model.forward(chunk)
            out = fade(out)
            final[:, :, :, start:end] += out
            if start == 0:
                fade.fade_in_len = int(overlap_frames)
                start += int(chunk_len - overlap_frames)
            else:
                start += chunk_len
            end += chunk_len
            if end >= length:
                fade.fade_out_len = 0
        return final

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Separate audio into Vocals and Instrumental tracks.")
    parser.add_argument("--input", required=True, help="Input audio file path")
    parser.add_argument("--output", required=True, help="Output directory for separated tracks")
    args = parser.parse_args()

    separator = AudioSeparation()
    separator.separate(args.input, args.output)