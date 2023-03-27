
import os

from dotenv import load_dotenv
from flask import Flask, request
from telegramBot import TelegramBot

load_dotenv()
app = Flask('ChatGPT-Telegram-Bot')
telegram_bot = TelegramBot(os.getenv('TELEGRAM_TOKEN'))


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    text = data.get('message', {}).get('text')
    chat_id = data.get('message', {}).get('chat', {}).get('id')

    telegram_bot.send_message({
        'chat_id': chat_id,
        'text': text,
    })
    return 'OK'


@app.route('/')
def home():
    return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
