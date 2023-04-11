from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pandas as pd

from models import OpenAIModel
from storage import FileStorage
from utils import query_similarity, construct_sections

import os
load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
model = OpenAIModel(os.getenv('OPENAI_API_KEY'))

STORAGE_FILE_NAME = os.getenv('STORAGE_FILE_NAME', 'embedding.json')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
CHAT_MODEL = os.getenv('CHAT_COMPLETION_MODEL', 'gpt-3.5-turbo')

file = FileStorage(STORAGE_FILE_NAME)
df = pd.read_csv(os.getenv('DOCS_PATH', 'taoyuan-airport-faq.csv'))
c_embedding = None


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        global c_embedding, df

        query = event.message.text.strip()
        q_embedding = model.embedding(query, EMBEDDING_MODEL)
        relevants = query_similarity(q_embedding, c_embedding)[:5]
        text = construct_sections(relevants, df)

        messages = [{
            'role': 'system',
            'content': '你現在非常會做問答題目，能夠透過文章找出答案'
        }, {
            'role': 'user',
            'content': f"""
            把問題誠實地回答，使用下面提供的上下文，如果答案不在以下文本中，請說“我不知道”。 
            上下文：{text}

            Q: {query}
            A:
            """
        }]

        _, content = model.chat_completion(messages, CHAT_MODEL)
    except Exception as e:
        print(str(e))
        content = '請重新輸入'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=content))


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


if __name__ == '__main__':
    if STORAGE_FILE_NAME in os.listdir('./'):
        c_embedding = file.load()
    else:
        c_embedding = {idx: model.embedding(f'{r.question}\n{r.answer}', EMBEDDING_MODEL) for idx, r in df.iterrows()}
        file.save(c_embedding)
    app.run(host='0.0.0.0', port=8080)
