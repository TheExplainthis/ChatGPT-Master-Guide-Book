
import os

from dotenv import load_dotenv
from flask import Flask, request
import opencc
from telegramBot import TelegramBot
from models import OpenAIModel


load_dotenv()
app = Flask('ChatGPT-Telegram-Bot')
s2t_converter = opencc.OpenCC('s2t')
telegram_bot = TelegramBot(os.getenv('TELEGRAM_TOKEN'))
model = OpenAIModel(api_key=os.getenv('OPENAI_API_KEY'))
CHAT_MODEL = os.getenv('CHAT_COMPLETION_MODEL', 'gpt-3.5-turbo')


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    text = data.get('message').get('text')
    chat_id = data.get('message').get('chat').get('id')

    messages = [{
        'role': 'system',
        'content': '你現在是一個生活小幫手'
    }, {
        'role': 'user',
        'content': text
    }]
    _, content = model.chat_completion(messages, CHAT_MODEL)
    content = s2t_converter.convert(content)
    telegram_bot.send_message({
        'chat_id': chat_id,
        'text': content,
    })
    return 'OK'


@app.route('/')
def home():
    return 'Hello World!'


if __name__ == '__main__':
    if os.getenv('SERVER_URL'):
        telegram_bot.set_webhook(os.getenv('SERVER_URL'))
    app.run(host='0.0.0.0', port=8080)
