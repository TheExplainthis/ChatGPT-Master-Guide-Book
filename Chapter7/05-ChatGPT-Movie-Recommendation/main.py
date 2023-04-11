from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage


from crawler import movie_crawler
from mongodb import mongodb
from models import OpenAIModel
from utils import save_movie_info, get_embedding_from_db, query_similarity, construct_sections
from lineComponent import line_component

from ast import literal_eval
import datetime
import os
import threading
load_dotenv()

app = Flask(__name__)

model = OpenAIModel(os.getenv('OPENAI_API_KEY'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
scheduler = BlockingScheduler()

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
CHAT_MODEL = os.getenv('CHAT_COMPLETION_MODEL', 'gpt-3.5-turbo')


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
    query = event.message.text.strip()
    try:
        movies = get_embedding_from_db(mongodb.db)
        c_embedding = {i: res['embedding'] for i, res in enumerate(movies)}
        q_embedding = model.embedding(query, EMBEDDING_MODEL)
        relevants = query_similarity(q_embedding, c_embedding)[:10]
        text = construct_sections(relevants, movies)

        messages = [{
            'role': 'system',
            'content': '你現在從用戶的喜好去找到推薦他的電影，請關注 story, anticipation, imdb_rate'
        }, {
            'role': 'user', 'content': f"""
            現在時間為：{str(datetime.datetime.now())}
            以下是當前院線電影資訊： {text}

            Q: 請推薦我 3 部電影，我的需求是：{query}
            A:

            回傳給我一個 List 裡面包含 index，
            回傳格式為：['...', '...', '...', '...']
            其他東西都不要說，不需要解釋，回傳 Array, List 格式
            """
        }]
        _, content = model.chat_completion(messages, CHAT_MODEL)
        try:
            indexes = literal_eval(content)
        except Exception:
            msg = TextSendMessage(text=content)
            line_bot_api.reply_message(event.reply_token, msg)
            return -1

        selected_movies = [movies[int(index)] for index in indexes if index.isdigit()]
        res = line_component.get_contents(selected_movies)
        msg = FlexSendMessage(alt_text='result', contents=res)
        line_bot_api.reply_message(event.reply_token, msg)
    except Exception:
        msg = TextSendMessage(text='請稍後再試')
        line_bot_api.reply_message(event.reply_token, msg)


@scheduler.scheduled_job('interval', days=1, id='update')
def update_data():
    db = mongodb.db
    movies = movie_crawler.get_movies(10)
    save_movie_info(movies, db, model, EMBEDDING_MODEL)


def start_scheduler():
    scheduler.start()


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


if __name__ == '__main__':
    mongodb.connect_to_database()
    if not mongodb.db['info'].find_one():
        print('Crawling... Please wait for three minutes.')
        update_data()
    t = threading.Thread(target=start_scheduler)
    t.start()
    app.run(host='0.0.0.0', port=8080)
