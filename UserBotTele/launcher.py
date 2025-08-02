import subprocess
import time
import os

base_path = "accounts"
bot_files = sorted(os.listdir(base_path))

processes = []
try:
    for folder in bot_files:
        if os.path.isdir(os.path.join(base_path, folder)):
            bot_path = os.path.join(base_path, folder, "main.py")
            print(f"Launching {bot_path}")
            p = subprocess.Popen(["python3", bot_path])
            processes.append(p)
            time.sleep(0.5)

    print("✅ All bots are running.")
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    print("\n🛑 Stopping all bots...")
    for p in processes:
        p.terminate()
