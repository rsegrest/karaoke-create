#!/usr/bin/env python3
"""Cross-platform script to kill processes listening on the application's ports."""

import sys
import subprocess
import signal
import os

PORTS = [5001, 5002, 5003, 5173, 5174, 5175]


def kill_on_ports_windows():
    for port in PORTS:
        try:
            result = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    pid = int(line.strip().split()[-1])
                    if pid > 0:
                        try:
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                           capture_output=True)
                            print(f"Killed process {pid} on port {port}")
                        except Exception:
                            pass
        except Exception as e:
            print(f"Error checking port {port}: {e}")


def kill_on_ports_unix():
    for port in PORTS:
        try:
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"],
                capture_output=True, text=True
            )
            for pid_str in result.stdout.strip().splitlines():
                pid = int(pid_str)
                try:
                    os.kill(pid, signal.SIGKILL)
                    print(f"Killed process {pid} on port {port}")
                except ProcessLookupError:
                    pass
        except Exception as e:
            print(f"Error checking port {port}: {e}")


if __name__ == "__main__":
    if sys.platform == "win32":
        kill_on_ports_windows()
    else:
        kill_on_ports_unix()
