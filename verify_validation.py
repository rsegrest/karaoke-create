import requests
import json
import time
import subprocess
import os
import signal
import sys

# Define the server URL
BASE_URL = "http://127.0.0.1:5001"

def start_server():
    """Starts the Flask server in a subprocess."""
    print("Starting server...")
    # Using python3 to run the app
    process = subprocess.Popen(
        ["python3", "queueing-proxy-svr/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid # Create a new session group
    )
    time.sleep(3) # Give server time to start
    return process

def stop_server(process):
    """Stops the Flask server."""
    print("Stopping server...")
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            print("Server process already stopped.")

def test_usage_endpoint():
    """Test the usage endpoint."""
    print("\nTesting usage endpoint (GET /)...")
    try:
        response = requests.get(BASE_URL + "/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Usage endpoint test PASSED")
        else:
            print("Usage endpoint test FAILED")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to server. Is it running?")

def test_queue_request_valid():
    """Test valid queue request with file."""
    print("\nTesting valid queue request (POST /queue_request) with file...")
    
    data = {
        "song_title": "Bohemian Rhapsody",
        "original_artist": "Queen",
        "performer_name": "Freddie"
    }
    
    # Create a dummy file
    with open("test_song.mp3", "w") as f:
        f.write("dummy audio content")

    files = {
        "music_file": ("test_song.mp3", open("test_song.mp3", "rb"))
    }
    
    try:
        response = requests.post(BASE_URL + "/queue_request", data=data, files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Valid request test PASSED")
            print(f"Response: {response.json()}")
        else:
            print("Valid request test FAILED")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Failed to connect to server.")
    finally:
        files["music_file"][1].close()
        os.remove("test_song.mp3")

def test_queue_request_missing_file():
    """Test queue request missing the file."""
    print("\nTesting missing file queue request (POST /queue_request)...")
    data = {
        "song_title": "Bohemian Rhapsody",
        "original_artist": "Queen",
        "performer_name": "Freddie"
    }
    
    try:
        response = requests.post(BASE_URL + "/queue_request", data=data) # No files
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("Missing file test PASSED")
            print(f"Response: {response.json()}")
        else:
            print("Missing file test FAILED")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Failed to connect to server.")

def main():
    server_process = None
    # Check if server is already running on port 5000
    try:
        requests.get(BASE_URL)
        print("Server appears to be running already.")
    except requests.exceptions.ConnectionError:
        server_process = start_server()

    try:
        test_usage_endpoint()
        test_queue_request_valid()
        test_queue_request_missing_file()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if server_process:
            stop_server(server_process)

if __name__ == "__main__":
    main()
