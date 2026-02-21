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
PROXY_SERVER_URL = os.getenv("PROXY_SERVER_URL")
MUSIC_SEPARATION_SERVER_URL = os.getenv("MUSIC_SEPARATION_SERVER_URL")
TRANSCRIPTION_SERVER_URL = os.getenv("TRANSCRIPTION_SERVER_URL")
GUI_URL = os.getenv("GUI_URL")

IS_WINDOWS = sys.platform == "win32"
VENV_PYTHON = ".venv\\Scripts\\python.exe" if IS_WINDOWS else "./.venv/bin/python"

print('URLs: ', PROXY_SERVER_URL, MUSIC_SEPARATION_SERVER_URL, TRANSCRIPTION_SERVER_URL, GUI_URL)

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

def start_queueing_proxy_server():
    """Starts the Flask server in a subprocess."""
    print("Starting Queueing Proxy server...")
    process = subprocess.Popen(
        [VENV_PYTHON, "app.py"],
        cwd="queueing-proxy-svr",
        **_popen_kwargs()
    )
    time.sleep(3) # Give server time to start
    return process

def start_music_separation_server():
    """Starts the music separation server in a subprocess."""
    print("Starting music separation server...")
    process = subprocess.Popen(
        [VENV_PYTHON, "app.py"],
        cwd="music-separation-svr",
        **_popen_kwargs()
    )
    time.sleep(3) # Give server time to start
    return process

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

def start_gui():
    """Starts the GUI in a subprocess."""
    print("Starting GUI...")
    kwargs = _popen_kwargs()
    if IS_WINDOWS:
        kwargs["shell"] = True  # yarn is a .cmd script on Windows
    process = subprocess.Popen(
        ["yarn", "start"],
        cwd="gui",
        **kwargs
    )
    time.sleep(3) # Give server time to start
    return process

def main():
    queueing_proxy_server_process = None
    music_separation_server_process = None
    transcription_server_process = None
    gui_process = None

    try:
        requests.get(PROXY_SERVER_URL)
        print("Queueing Proxy server appears to be running already.")
    except requests.exceptions.ConnectionError:
        queueing_proxy_server_process = start_queueing_proxy_server()
    try:
        requests.get(MUSIC_SEPARATION_SERVER_URL)
        print("Music separation server appears to be running already.")
    except requests.exceptions.ConnectionError:
        music_separation_server_process = start_music_separation_server()
    try:
        requests.get(TRANSCRIPTION_SERVER_URL)
        print("Transcription server appears to be running already.")
    except requests.exceptions.ConnectionError:
        transcription_server_process = start_transcription_server()
    try:
        requests.get(GUI_URL)
        print("GUI appears to be running already.")
    except requests.exceptions.ConnectionError:
        gui_process = start_gui()

    input("Press Enter to stop all servers...")
    _stop_process(queueing_proxy_server_process, "Queueing Proxy server")
    _stop_process(music_separation_server_process, "Music separation server")
    _stop_process(transcription_server_process, "Transcription server")
    _stop_process(gui_process, "GUI")

if __name__ == "__main__":
    main()
