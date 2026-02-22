import requests
import time
import os
import sys

def test_pipeline():
    # 1. Start processing
    url = "http://localhost:5001/queue_request"
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None

    # Find an audio file to test if none provided
    if not audio_path:
        shared_uploads = os.path.join("shared_data", "uploads")
        if os.path.exists(shared_uploads):
            files = [f for f in os.listdir(shared_uploads) if f.endswith('.m4a') or f.endswith('.mp3')]
            if files:
                audio_path = os.path.join(shared_uploads, files[0])
    
    if not audio_path or not os.path.exists(audio_path):
        print(f"Could not find an audio file to test. Put one in shared_data/uploads/ or pass it as an arg.")
        return

    print(f"Testing with audio file: {audio_path}")
    
    data = {
        'song_title': 'Automation Test',
        'performer_name': 'Test Runner',
        'original_artist': 'System'
    }

    with open(audio_path, 'rb') as f:
        files = {'music_file': (os.path.basename(audio_path), f, 'audio/mp4')}
        print("Sending request to /queue_request...")
        response = requests.post(url, data=data, files=files)

    if response.status_code != 201:
        print(f"Failed to queue request: {response.status_code}")
        print(response.text)
        return

    result = response.json()
    song_id = result['song_id']
    print(f"Successfully queued song! ID: {song_id}")

    # 2. Poll for completion
    status_url = f"http://localhost:5001/get_song_data?song_id={song_id}"
    
    print("Waiting for processing to complete...")
    max_retries = 120 # 2 minutes timeout (it takes a while for separation and transcription)
    for i in range(max_retries):
        resp = requests.get(status_url)
        if resp.status_code == 200:
            data = resp.json()
            status = data['status']
            print(f"[{i}/{max_retries}] Status: {status}")
            
            if status == 'done':
                print("Processing completed successfully!")
                
                # Check artifacts
                output_dir = os.path.join("shared_data", "outputs", str(song_id))
                print(f"\nChecking artifacts in {output_dir}:")
                if os.path.exists(output_dir):
                    print("Directory exists.")
                    for f in os.listdir(output_dir):
                        print(f"  - {f}")
                else:
                    print("ERROR: Output directory does not exist!")
                
                return
            elif status.startswith('error'):
                print(f"Processing failed with status: {status}")
                return
            
        time.sleep(5)
        
    print("Timeout waiting for processing to complete.")

if __name__ == "__main__":
    test_pipeline()
