#from dotenv import load_dotenv
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
import openai

# Load environment variables
#load_dotenv()
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)

# Reference storage class
class Reference:
    """Stores previous response from the chatbot."""
    def __init__(self):
        self.response = ""  # Fix: was incorrectly named `reference`

reference = Reference()
MODEL_NAME = "gpt-3.5-turbo"

# Function to clear past response
def clear_past():
    reference.response = ""

# /start command handler
@dispatcher.message_handler(commands=["start"])
async def command_start_handler(message: types.Message):
    await message.reply("Hi, I'm Srishti. How may I assist you today?")

# /help command to clear context
@dispatcher.message_handler(commands=["help"])
async def command_help_handler(message: types.Message):
    clear_past()
    await message.reply("I've cleared the past conversation and context.")

# Main message handler
@dispatcher.message_handler(lambda message: not message.text.startswith('/'))
async def message_handler(message: types.Message):
    logging.info(f">>> USER: {message.text}")

    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "assistant", "content": reference.response},
                {"role": "user", "content": message.text}
            ]
        )
        reply_text = response['choices'][0]['message']['content']
        reference.response = reply_text  # store assistant's latest response
        await bot.send_message(chat_id=message.chat.id, text=reply_text)

    except Exception as e:
        logging.error(f"Error from OpenAI: {e}")
        await message.reply("Sorry, something went wrong.")

# Start the bot
if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
