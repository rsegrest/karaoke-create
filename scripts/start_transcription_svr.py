#!/usr/bin/env python3

import requests
import time
import subprocess
import os
import signal
import dotenv
import json
import sys

# Load environment variables from .env file
dotenv.load_dotenv()

# Define the server URL
TRANSCRIPTION_SERVER_URL = os.getenv("TRANSCRIPTION_SERVER_URL")

IS_WINDOWS = sys.platform == "win32"
VENV_PYTHON = ".venv\\Scripts\\python.exe" if IS_WINDOWS else "./.venv/bin/python"

print('URLs: ', TRANSCRIPTION_SERVER_URL)

def _popen_kwargs():
    """Returns platform-specific kwargs for subprocess.Popen to create a new process group."""
    if IS_WINDOWS:
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    else:
        return {"preexec_fn": os.setsid}

def _stop_process(process, name):
    """Stops a subprocess in a cross-platform way."""
    print(f"Stopping {name}...")
    if not process:
        return
    try:
        if IS_WINDOWS:
            process.terminate()
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except (ProcessLookupError, OSError):
        print(f"{name} process already stopped.")

def start_transcription_server():
    """Starts the transcription server in a subprocess."""
    print("Starting transcription server...")
    process = subprocess.Popen(
        [VENV_PYTHON, "app.py"],
        cwd="transcription_svr",
        **_popen_kwargs()
    )
    time.sleep(3) # Give server time to start
    return process

def main():
    transcription_server_process = None

    try:
        requests.get(TRANSCRIPTION_SERVER_URL)
        print("Transcription server appears to be running already.")
    except requests.exceptions.ConnectionError:
        transcription_server_process = start_transcription_server()
    try:
        requests.get(TRANSCRIPTION_SERVER_URL)
        print("Transcription server appears to be running already.")
    except requests.exceptions.ConnectionError:
        transcription_server_process = start_transcription_server()

    input("Press Enter to stop transcription server...")
    _stop_process(transcription_server_process, "Transcription server")

if __name__ == "__main__":
    main()
