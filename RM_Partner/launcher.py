import subprocess
import time

# List of bot scripts to run
bot_files = [
    "amoyrm1.py",
    "amoyrm3.py",
    "shell1.py",
]

# Store subprocesses here
processes = []

try:
    for bot in bot_files:
        print(f"Launching {bot}...")
        p = subprocess.Popen(["python", bot], stdout=open(f"{bot}.log", "w"), stderr=subprocess.STDOUT)
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
