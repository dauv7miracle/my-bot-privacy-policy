from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os
import requests
import json
from datetime import datetime

def log_user(update: Update, bot_name: str):
    user = update.effective_user
    log_dir = "user_logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/{bot_name}.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | ID: {user.id} | Username: @{user.username} | Name: {user.full_name}\n")

TOKEN = os.getenv("TELEGRAM_TOKEN") # <<< IMPORTANT: Replaced with your actual bot token

# --- LLM Integration ---
# LLM_API_URL points to your Ollama container's API
# The default port for Ollama is 11434
# Using /api/chat for better persona control
LLM_API_URL = os.getenv("LLM_API_URL", "http://ollama:11434/api/chat")

def get_llm_response(prompt_text: str, model_name: str = "llama3.2") -> str:
    # System message to set the persona and fallback behavior
    system_message = {
        "role": "system",
        "content": (
            "You are Meta AI, a helpful and friendly AI assistant. "
            "Always introduce yourself as Meta AI when asked or when starting a new conversation. "
            "If you are unable to understand a request, or cannot provide a satisfactory answer, "
            "please politely state that you cannot fulfill the request and suggest the user contact "
            "<a href=\"https://t.me/davmrcl\">Dauv Miracle</a> for further assistance. "
            "Keep your responses concise and to the point."
        )
    }

    messages = [
        system_message,
        {"role": "user", "content": prompt_text}
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False, # We want the full response at once
        "options": {"temperature": 0.7} # Adjust for creativity (0.0-1.0)
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=180) # Increased timeout for LLM
        response.raise_for_status() # Raise an exception for HTTP errors
        response_data = response.json()
        # The exact path to the content varies by LLM API. Adjust this line if needed.
        return response_data.get("message", {}).get("content", "No response from LLM.")
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API: {e}")
        return "🤖 Sorry, I'm having trouble connecting to my AI brain right now. Please try again later."
    except (KeyError, IndexError) as e:
        print(f"Unexpected LLM response format or missing key: {e}\nResponse: {response_data}")
        return "🤖 I received an unexpected response from my AI brain. Please try rephrasing your request."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "🤖 An unknown error occurred while processing your request."

# --- Bot Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user(update, "ollama_tbot") # Log user for this bot
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    initial_message = get_llm_response("Introduce yourself and list your capabilities.")
    await update.message.reply_html(initial_message) # Use reply_html for the link

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide text to translate. Usage: /translate <your text>")
        return

    text_to_translate = " ".join(context.args)
    prompt = f"Translate the following text to English: {text_to_translate}"

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    translated_text = get_llm_response(prompt)
    await update.message.reply_html(f"Translated: {translated_text}") # Use reply_html for potential links

async def generate_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "I'm a text-based AI model (Llama 3.2), so I can't generate images directly.<br>"
        "To generate images, you would typically need a separate image generation AI (like DALL-E, Stable Diffusion, or Midjourney) and its API. "
        "You could integrate such a service into this bot if you have access to one! "
        "If you need more information, please contact <a href=\"https://t.me/davmrcl\">Dauv Miracle</a>."
    )

async def zodiac_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide your zodiac sign. Usage: /zodiac <your zodiac sign>")
        return

    zodiac_sign = " ".join(context.args).strip().title() # Capitalize first letter
    prompt = f"Give me a short, positive fortune telling for today for a {zodiac_sign}. "

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    fortune_text = get_llm_response(prompt)
    await update.message.reply_html(f"Your {zodiac_sign} fortune: {fortune_text}") # Use reply_html for potential links

async def general_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This handles any text message that is not a command
    user_message = update.message.text
    if user_message:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        llm_reply = get_llm_response(user_message)
        await update.message.reply_html(llm_reply) # Use reply_html for potential links

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("translate", translate_command))
    app.add_handler(CommandHandler("generateimage", generate_image_command))
    app.add_handler(CommandHandler("zodiac", zodiac_command))

    # Message Handler for non-command text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message_handler))

    app.run_polling()
