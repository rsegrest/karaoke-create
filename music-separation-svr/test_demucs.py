import sys
import os

try:
    from demucs.api import Separator
    print("Demucs API imported successfully.")
except ImportError as e:
    print(f"Failed to import demucs: {e}")
    sys.exit(1)

def test_demucs():
    input_file = "/Users/ricksegrest/code/2026/karaoke-create/shared_data/uploads/real_test_file.wav"
    print(f"Testing demucs separation on {input_file}")
    
    # Initialize the separator. `htdemucs` or `htdemucs_ft` are the best models.
    # We will use htdemucs for speed but good quality, or htdemucs_ft for the absolute best quality.
    separator = Separator(model="htdemucs_ft", device="cpu")
    print("Separator model loaded successfully.")
    
    # Run separation
    origin, separated = separator.separate_audio_file(input_file)
    print("Separation complete.")
    
    # separated is a dict: {'vocals': Tensor, 'drums': Tensor, 'bass': Tensor, 'other': Tensor}
    print(f"Stems output: {list(separated.keys())}")
    
    # Verify shape
    print(f"Vocals tensor shape: {separated['vocals'].shape}")

if __name__ == '__main__':
    test_demucs()
