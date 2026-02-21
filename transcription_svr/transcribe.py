import json
import csv
import sys
import torch
from qwen_asr import Qwen3ASRModel

# global singleton to prevent concurrent OOM crashes
print("Initializing Qwen3 ASR Model into global memory. This may take a moment...")
MODEL = Qwen3ASRModel.from_pretrained(
    "Qwen/Qwen3-ASR-1.7B", 
    forced_aligner="Qwen/Qwen3-ForcedAligner-0.6B",
    torch_dtype=torch.float32
)

# Explicitly move the inner PyTorch model and aligner to CPU
MODEL.model.to("cpu")
if MODEL.forced_aligner:
    MODEL.forced_aligner.model.to("cpu")
print("Model initialized successfully!")

def transcribe_to_structured_data(audio_file, output_name):
    """
    Transcribes audio using Qwen3-ASR and saves the results 
    with timestamps to both JSON and CSV files.
    """
    # Transcribe with the timestamp flag set to True
    print(f"Processing: {audio_file}...")
    results = MODEL.transcribe(audio_file, return_time_stamps=True)

    # Convert results into a serializable list
    data_to_save = []
    for transcription in results:
        if transcription.time_stamps is not None:
            for item in transcription.time_stamps:
                data_to_save.append({
                    "start": item.start_time,
                    "end": item.end_time,
                    "text": item.text.strip()
                })
        else:
             data_to_save.append({
                "start": 0.0,
                "end": 0.0,
                "text": transcription.text.strip()
            })

    txt_path = f"{output_name}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        lyrics_txt = ""
        for transcription in results:
            print('writing transcription: ')
            print(transcription.text)
            f.write(f"{transcription.text.strip()}\n")
            lyrics_txt += transcription.text.strip() + "\n"
    # Save to JSON
    json_path = f"{output_name}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

    # Save to CSV
    csv_path = f"{output_name}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["start", "end", "text"])
        writer.writeheader()
        writer.writerows(data_to_save)

    return json_path, csv_path, lyrics_txt

if __name__ == "__main__":
    # Usage: python script.py my_audio.mp3 output_filename
    if len(sys.argv) > 1:
        json_path, csv_path, lyrics_txt = transcribe_to_structured_data(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "output")
    else:
        print("Please provide an audio file path.")
