import subprocess
import time
import os
import sys

# Path to the python executable in the virtual environment
# On Windows, it's in 'Scripts'; on Linux/macOS, it's in 'bin'.
VENV_DIR = ".venv"
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")

if not os.path.exists(VENV_PYTHON):
    print(f"❌ ERROR: Python interpreter not found at {os.path.abspath(VENV_PYTHON)}")
    sys.exit("Please run this script from the 'A2' directory containing the '.venv' folder.")

# List of bot scripts to run
bot_files = [
    "ang1.py",
    "ang2.py",
    "ang3.py",
    "ang4.py",
    "ang5.py",
    "ang6.py",
    "ang7.py",
    "ang8.py",
    "ang9.py",
    "ang10.py",
    "ang11.py",
    "ang12.py",
    "ang13.py",
    "ang14.py",
    "ang15.py",
    "ang16.py",
    "ang17.py",
    "ang18.py",
]

# Store subprocesses here
processes = []

try:
    for bot in bot_files:
        print(f"Launching {bot}...")
        p = subprocess.Popen([VENV_PYTHON, bot], stdout=open(f"{bot}.log", "w"), stderr=subprocess.STDOUT)
        processes.append((bot, p))
        time.sleep(1)  # Slight delay to avoid overload

    print("✅ All bots are running. BY Dauv Miracle.")

    # Keep launcher alive
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    print("\n🛑 Stopping all bots...")
    for bot, p in processes:
        print(f"Terminating {bot}...")
        p.terminate()
    print("✅ All bots stopped.")
