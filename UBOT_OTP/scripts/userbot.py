import json
from pyrogram import Client

# Load account details
with open("../config/accounts.json", "r") as f:
    accounts = json.load(f)

# Function to retrieve OTPs
def get_otp(phone_number, session_string):
    app = Client(phone_number, session_string=session_string)
    app.start()
    print(f"Logged in as {phone_number}")

    # Retrieve OTPs from messages
    for message in app.get_chat_history("Telegram"):
        if "code" in message.text:
            print(f"OTP for {phone_number}: {message.text}")
            break

    app.stop()

# Main script
if __name__ == "__main__":
    for account in accounts:
        get_otp(account["phone_number"], account["session_string"])
