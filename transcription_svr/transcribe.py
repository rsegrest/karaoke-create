import json
import csv
import sys
import torch
from qwen_asr import Qwen3ASRModel
from pathlib import Path

# global singleton to prevent concurrent OOM crashes
print("Initializing Qwen3 ASR Model into global memory. This may take a moment...")
MODEL = Qwen3ASRModel.from_pretrained(
    "Qwen/Qwen3-ASR-1.7B", 
    forced_aligner="Qwen/Qwen3-ForcedAligner-0.6B",
    dtype=torch.float32
)

# Determine the best available device (use CUDA if on an NVIDIA GPU, fallback to CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Move the inner PyTorch model and aligner to the selected device
MODEL.model.to(device)
if hasattr(MODEL, "forced_aligner") and MODEL.forced_aligner:
    MODEL.forced_aligner.model.to(device)
print("Model initialized successfully!")

def transcribe_to_structured_data(audio_file, output_dir, output_name):
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
    # Create text file with one line per phrase
    txt_filename = f"{output_name}.txt"
    txt_path = Path(output_dir) / txt_filename
    with open(txt_path, 'w', encoding='utf-8') as f:
        lyrics_txt = ""
        
        # Iterate over results to align punctuation from raw transcription text with timestamps
        for transcription in results:
            if not transcription.text:
                continue
                
            raw_text = transcription.text.strip()
            
            # If no timestamps available, just use regex to break on punctuation
            if transcription.time_stamps is None:
                import re
                lyrics_txt += re.sub(r'([,.;?!])\s+', r'\1\n', raw_text) + "\n"
                continue

            current_line = ""
            last_end = 0.0
            search_idx = 0
            
            for item in transcription.time_stamps:
                word = item.text.strip()
                start = item.start_time
                end = item.end_time
                
                # Break phrase on long pause (> 1.0 seconds)
                if current_line and end > 0 and (start - last_end) > 1.0:
                    lyrics_txt += current_line.strip() + "\n"
                    current_line = ""
                    
                word_idx = raw_text.find(word, search_idx)
                punct = ""
                if word_idx >= 0:
                    end_of_word = word_idx + len(word)
                    while end_of_word < len(raw_text) and raw_text[end_of_word] in ",.;?!":
                        punct += raw_text[end_of_word]
                        end_of_word += 1
                    search_idx = end_of_word

                if current_line:
                    current_line += " " + word + punct
                else:
                    current_line += word + punct
                    
                last_end = end
                
                # Break phrase on punctuation (either extracted or intrinsic)
                if punct or (word and word[-1] in ",.;?!"):
                    lyrics_txt += current_line.strip() + "\n"
                    current_line = ""

            if current_line:
                lyrics_txt += current_line.strip() + "\n"

        # Clean up empty lines and trailing spaces
        lyrics_txt = "\n".join([line.strip() for line in lyrics_txt.splitlines() if line.strip()]) + "\n"

        print("writing transcription:\n" + lyrics_txt)
        f.write(lyrics_txt)

    # Save to JSON
    json_filename = f"{output_name}.json"
    json_path = Path(output_dir) / json_filename
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

    # Save to CSV
    csv_filename = f"{output_name}.csv"
    csv_path = Path(output_dir) / csv_filename
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["start", "end", "text"])
        writer.writeheader()
        writer.writerows(data_to_save)

    return str(json_path), str(csv_path), lyrics_txt

if __name__ == "__main__":
    # Usage: python script.py my_audio.mp3 output_dir output_filename
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
        output_name = sys.argv[3] if len(sys.argv) > 3 else "output"
        json_path, csv_path, lyrics_txt = transcribe_to_structured_data(sys.argv[1], output_dir, output_name)
    else:
        print("Please provide an audio file path and output directory.")
