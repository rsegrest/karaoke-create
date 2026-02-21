import subprocess
import time
import requests

with open("transcribe_stdout.log", "w") as out, open("transcribe_stderr.log", "w") as err:
    transcribe = subprocess.Popen(["./.venv/bin/python", "app.py"], cwd="transcription_svr", stdout=out, stderr=err)
    print("Transcribe started")
    
    # Wait for server to actually be responding
    for _ in range(20):
        try:
            r = requests.get("http://localhost:5003/", timeout=1)
            break
        except:
            time.sleep(1)

    try:
        with open("shared_data/uploads/test_integration.mp3", "rb") as f:
            print("Sending audio to transcribe...")
            r = requests.post("http://localhost:5003/transcribe", files={"music_file": f})
            print("Status Code:", r.status_code)
            print("Response text length:", len(r.text))
            print("Response:", r.text)
    except Exception as e:
        print("Request failed:", e)

    time.sleep(2)
    transcribe.kill()
