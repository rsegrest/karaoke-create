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

def start_queueing_proxy_server():
    """Starts the Flask server in a subprocess."""
    print("Starting Queueing Proxy server...")
    process = subprocess.Popen(
        ["./.venv/bin/python", "app.py"],
        cwd="queueing-proxy-svr",
        preexec_fn=os.setsid # Create a new session group
    )
    time.sleep(3) # Give server time to start
    return process

def start_music_separation_server():
    """Starts the music separation server in a subprocess."""
    print("Starting music separation server...")
    process = subprocess.Popen(
        ["./.venv/bin/python", "app.py"],
        cwd="music-separation-svr",
        preexec_fn=os.setsid # Create a new session group
    )
    time.sleep(3) # Give server time to start
    return process

def start_transcription_server():
    """Starts the transcription server in a subprocess."""
    print("Starting transcription server...")
    process = subprocess.Popen(
        ["./.venv/bin/python", "app.py"],
        cwd="transcription_svr",
        preexec_fn=os.setsid # Create a new session group
    )
    time.sleep(3) # Give server time to start
    return process

def start_gui():
    """Starts the GUI in a subprocess."""
    print("Starting GUI...")
    process = subprocess.Popen(
        ["yarn", "start"],
        cwd="gui",
        preexec_fn=os.setsid # Create a new session group
    )
    time.sleep(3) # Give server time to start
    return process

def stop_queueing_proxy_server(process):
    """Stops the Queueing Proxy server."""
    print("Stopping Queueing Proxy server...")
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            print("Queueing Proxy server process already stopped.")

def stop_music_separation_server(process):
    """Stops the music separation server."""
    print("Stopping music separation server...")
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            print("Music separation server process already stopped.")

def stop_transcription_server(process):
    """Stops the transcription server."""
    print("Stopping transcription server...")
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            print("Transcription server process already stopped.")

def stop_gui(process):
    """Stops the GUI."""
    print("Stopping GUI...")
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            print("GUI process already stopped.")

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
    stop_queueing_proxy_server(queueing_proxy_server_process)
    stop_music_separation_server(music_separation_server_process)
    stop_transcription_server(transcription_server_process)
    stop_gui(gui_process)

if __name__ == "__main__":
    main()
