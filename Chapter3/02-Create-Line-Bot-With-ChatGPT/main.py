from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from dotenv import load_dotenv
import openai
import os
load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_TOKEN')

messages = [{
    'role': 'system', 'content': os.getenv('OPENAI_SYSTEM_MESSAGE')
}]


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text.startswith('/清除'):
        messages = [{
            'role': 'system', 'content': os.getenv('OPENAI_SYSTEM_MESSAGE')
        }]
        response = '歷史紀錄清除成功'
    else:
        messages.append({
            'role': 'user', 'content': event.message.text
        })
        response = openai.ChatCompletion.create(
            model=os.getenv('OPENAI_MODEL_ENGINE'),
            messages=messages
        )
        role = response['choices'][0]['message']['role']
        content = response['choices'][0]['message']['content']
        messages.append({
            'role': role, 'content': content
        })
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))


@app.route("/", methods=['GET'])
def home():
    return 'Hello World!'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
