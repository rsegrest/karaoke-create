import requests
import json
import time
import subprocess
import os
import signal
import sys

# Define the server URLs
PROXY_URL = "http://127.0.0.1:5001"
SEPARATION_URL = "http://127.0.0.1:5002"
TRANSCRIPTION_URL = "http://127.0.0.1:5003"

def start_services():
    """Starts the Flask servers in subprocesses."""
    print("Starting proxy server...")
    proxy_process = subprocess.Popen(
        ["python3", "queueing-proxy-svr/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # We assume separation and transcription services are already running or we can start them.
    # For full test, we should start them.
    # However, transcription service relies on large models (Qwen) so starting it might be slow.
    # The user seems to be running them manually. 
    # Let's try to connect to them first.
    return proxy_process

def stop_services(proxy):
    """Stops the proxy server."""
    print("Stopping proxy server...")
    if proxy:
        try:
            os.killpg(os.getpgid(proxy.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass

def test_full_integration():
    """Test the full flow with a small dummy file."""
    print("\nTesting full integration flow (Proxy -> Separation + Transcription)...")
    
    data = {
        "song_title": "Test Song",
        "original_artist": "Test Artist",
        "performer_name": "Test Performer"
    }
    
    # Create a dummy file (mp3)
    # Note: Transcription service might fail on dummy file if it expects real audio.
    # But we want to test connectivity and file passing, so let's see.
    # FFmpeg might error on invalid mp3.
    # Let's create a minimal valid wav or mp3 if possible, or use a test file if available.
    # The user used "11_You_Decorated_My_Life.m4a" in their test.
    # We'll use a dummy for now and expect a 500 from transcription if it fails decoding,
    # but NOT a 400 "Invalid file type".
    
    with open("test_integration.mp3", "w") as f:
        f.write("dummy audio content")

    files = {
        "music_file": ("test_integration.mp3", open("test_integration.mp3", "rb"))
    }
    
    try:
        start_time = time.time()
        print("Sending request to proxy...")
        response = requests.post(PROXY_URL + "/queue_request", data=data, files=files)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {end_time - start_time:.2f}s")
        print(f"Response: {response.json()}")

        # Check if response contains expected keys
        json_resp = response.json()
        
        # We expect keys for both services
        expected_keys = ['accompanyment_file', 'vocal_file', 'lyrics_txt', 'lyrics_json']
        missing_keys = [k for k in expected_keys if k not in json_resp]
        
        if not missing_keys:
            print("Integration test PASSED (Response structure valid)")
        else:
            print(f"Integration test FAILED (Missing keys: {missing_keys})")

    except requests.exceptions.ConnectionError:
        print("Failed to connect to proxy server.")
    finally:
        files["music_file"][1].close()
        os.remove("test_integration.mp3")

def main():
    # Kill any existing verification proxy on 5001 (but not the user's if they are running it)
    # The user said they are running python app.py in the directories.
    # If they are running on 5001, 5002, 5003, we should just test against them.
    
    try:
        requests.get(PROXY_URL)
        print("Proxy appears to be running already. Testing against it.")
        test_full_integration()
    except requests.exceptions.ConnectionError:
        print("Proxy not running. Starting temporary proxy...")
        proxy_proc = start_services()
        try:
            test_full_integration()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            stop_services(proxy_proc)

if __name__ == "__main__":
    main()
