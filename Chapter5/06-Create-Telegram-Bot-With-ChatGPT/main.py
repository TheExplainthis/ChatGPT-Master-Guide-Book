
import os

from dotenv import load_dotenv
from flask import Flask, request
import opencc
from telegramBot import TelegramBot
from models import OpenAIModel


load_dotenv()
app = Flask('ChatGPT-Telegram-Bot')
telegram_bot = TelegramBot(os.getenv('TELEGRAM_TOKEN'))
s2t_converter = opencc.OpenCC('s2t')
model = OpenAIModel(api_key=os.getenv('OPENAI_API_TOKEN'), model_engine=os.getenv('OPENAI_MODEL_ENGINE'))


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    text = data.get('message', {}).get('text')
    chat_id = data.get('message', {}).get('chat', {}).get('id')

    messages = [{
        'role': 'system', 'content': os.getenv('OPENAI_SYSTEM_MESSAGE')
    }, {
        'role': 'user', 'content': text
    }]
    _, content = model.chat_completion(messages)
    content = s2t_converter.convert(content)
    telegram_bot.send_message({
        'chat_id': chat_id,
        'text': content,
    })
    return 'OK'


@app.route('/')
def home():
    return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
