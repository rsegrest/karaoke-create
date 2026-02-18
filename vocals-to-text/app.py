import json
import csv
import sys
from qwen_asr import Qwen3ASRModel

def transcribe_to_structured_data(audio_path, output_name):
    """
    Transcribes audio using Qwen3-ASR and saves the results 
    with timestamps to both JSON and CSV files.
    """
    # Load the model (0.6B is efficient; 1.7B is more accurate)
    # model = Qwen3ASRModel.from_pretrained("Qwen/Qwen3-ASR-0.6B", forced_aligner="Qwen/Qwen3-ForcedAligner-0.6B")
    model = Qwen3ASRModel.from_pretrained("Qwen/Qwen3-ASR-1.7B", forced_aligner="Qwen/Qwen3-ForcedAligner-0.6B")

    # Transcribe with the timestamp flag set to True
    print(f"Processing: {audio_path}...")
    results = model.transcribe(audio_path, return_time_stamps=True)

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
        for transcription in results:
            print('writing transcription: ')
            print(transcription.text)
            f.write(f"{transcription.text.strip()}\n")
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

    print(f"Done! Files saved: \n - {json_path} \n - {csv_path}")

if __name__ == "__main__":
    # Usage: python script.py my_audio.mp3 output_filename
    if len(sys.argv) > 1:
        transcribe_to_structured_data(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "output")
    else:
        print("Please provide an audio file path.")
