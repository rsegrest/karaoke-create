import torch
from qwen_asr import Qwen3ASRModel

print("Loading model...")
try:
    model = Qwen3ASRModel.from_pretrained(
        "Qwen/Qwen3-ASR-1.7B",
        forced_aligner="Qwen/Qwen3-ForcedAligner-0.6B",
        torch_dtype=torch.float32,
    )
    print("Model loaded.")
    print("Base model device:", model.model.device)
    print("Forced aligner model device:", model.forced_aligner.model.device)
    
    # Try moving to cpu explicitly without empty device map
    model.model.to("cpu")
    model.forced_aligner.model.to("cpu")
    print("Moved to CPU successfully.")
    
    print("Transcribing audio...")
    results = model.transcribe(
        "shared_data/uploads/real_test_file.wav",
        return_time_stamps=True
    )
    print("Transcription successful!", results[0].text[:50])
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
