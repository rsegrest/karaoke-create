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

# def start_services():
#     """Starts the Flask servers in subprocesses."""
#     print("Starting proxy server...")
#     proxy_process = subprocess.Popen(
#         ["python3", "queueing-proxy-svr/app.py"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         preexec_fn=os.setsid
#     )
    
#     print("Starting separation server...")
#     # Redirect output to file for debugging
#     with open("separation_svr.log", "w") as out:
#         sep_process = subprocess.Popen(
#             ["python3", "music-separation-svr/app.py"],
#             stdout=out,
#             stderr=subprocess.STDOUT, # Merge stderr into stdout
#             preexec_fn=os.setsid
#         )
    
#     # Wait longer for model download/load
#     print("Waiting 30s for services to start...")
#     time.sleep(30) 
#     return proxy_process, sep_process

# def stop_services(proxy, sep):
#     """Stops the Flask servers."""
#     print("Stopping servers...")
#     if proxy:
#         try:
#             os.killpg(os.getpgid(proxy.pid), signal.SIGTERM)
#         except ProcessLookupError:
#             pass
#     if sep:
#         try:
#             os.killpg(os.getpgid(sep.pid), signal.SIGTERM)
#         except ProcessLookupError:
#             pass

def test_integration():
    """Test the full flow with a small dummy file."""
    print("\nTesting full integration flow...")
    
    data = {
        "song_title": "Test Song",
        "original_artist": "Test Artist",
        "performer_name": "Test Performer"
    }
    
    # Create a dummy file
    # with open("test_integration.mp3", "w") as f:
    #     f.write("dummy audio content")

    files = {
        # "music_file": ("test_integration.mp3", open("test_integration.mp3", "rb"))
        "music_file": ("11_You_Decorated_My_Life.m4a", open("queueing-proxy-svr/testsongs/11_You_Decorated_My_Life.m4a", "rb"))
    }
    
    try:
        start_time = time.time()
        print("Sending request to proxy...")
        response = requests.post(PROXY_URL + "/queue_request", data=data, files=files)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {end_time - start_time:.2f}s")
        print(f"Response: {response.json()}")

        # Check if response contains expected keys (even if they are error messages from the mock execution)
        json_resp = response.json()
        if 'accompanyment_file' in json_resp and 'vocal_file' in json_resp:
            print("Integration test PASSED (Response structure valid)")
        else:
            print("Integration test FAILED (Missing expected keys)")

    except requests.exceptions.ConnectionError:
        print("Failed to connect to proxy server.")
    finally:
        files["music_file"][1].close()
        # os.remove("test_integration.mp3")

def main():
    # Kill any existing on these ports
    # subprocess.run("lsof -t -i:5001 -i:5002 | xargs kill", shell=True)
    
    # proxy_proc, sep_proc = start_services()
    try:
        test_integration()
    except Exception as e:
        print(f"An error occurred: {e}")
    # finally:
        # stop_services(proxy_proc, sep_proc)

if __name__ == "__main__":
    main()
