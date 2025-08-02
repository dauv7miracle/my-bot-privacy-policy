#!/usr/bin/env python3

import subprocess
VENV_PYTHON = "/home/naga7miracle/UbotGcloud-v.1/A1/.venv/bin/python"

def start_bot(script_path, bot_name):
    command = ["pm2", "start", script_path, "--name", bot_name, "--interpreter", VENV_PYTHON]
    try:
        subprocess.run(command, check=True)
        print(f"Started {bot_name} using PM2")
    except subprocess.CalledProcessError as e:
        print(f"Error starting {bot_name}: {e}")

if __name__ == "__main__":
    
    start_bot("/home/naga7miracle/UbotGcloud-v.1/A1/main.py", "Ubot_A1")
    start_bot("/home/naga7miracle/UbotGcloud-v.1/RM_Partner/main.py", "RM_A1")
    start_bot("/home/naga7miracle/UbotGcloud-v.1/multi_bot_launcher/amoyrm1.py", "AmoyRM_A1")
    start_bot("/home/naga7miracle/UbotGcloud-v.1/multi_bot_launcher/amoyrm2.py", "AmoyRM_A2")
    start_bot("/home/naga7miracle/UbotGcloud-v.1/SGP1/sgbot.py", "SG_A1")

    print("All bots started (or attempted to start).")
