from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationSendMessage

import pandas as pd
import requests


from models import OpenAIModel
from storage import FileStorage
from utils import query_similarity, construct_sections, construct_result

from ast import literal_eval
import datetime
import os
import threading
load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
model = OpenAIModel(os.getenv('OPENAI_API_KEY'))
scheduler = BlockingScheduler()

STORAGE_FILE_NAME = os.getenv('STORAGE_FILE_NAME', 'embedding.json')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
CHAT_MODEL = os.getenv('CHAT_COMPLETION_MODEL', 'gpt-3.5-turbo')

file = FileStorage(STORAGE_FILE_NAME)
parking_df = pd.read_csv(os.getenv('DOCS_PATH', 'TCMSV_alldesc.csv'))
df = None
c_embedding = None
parking_avail = None


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
        relevants = query_similarity(q_embedding, c_embedding)[:15]
        text = construct_sections(relevants, df)

        messages = [{
            'role': 'system',
            'content': '你現在非常會從眾多停車場當中，找到適合用戶需求的停車場'
        }, {
            'role': 'user',
            'content': f"""
            以下是當前停車場資訊： {text}
            且現在時間為：{str(datetime.datetime.now())}

            Q: 現要在要找停車位，需求為：{query} 、\n 空位數 必須大於 0，且正在營業的停車場
            A:

            回傳給我一個陣列，裡面為停車場名稱，例如：['...', '...', '...']，其他東西都不要說
            """
        }]

        _, content = model.chat_completion(messages, CHAT_MODEL)
        try:
            arr = literal_eval(content)
            parking_infos = construct_result(df, arr)
            t = parking_avail['data']['UPDATETIME']
            msgs = [TextSendMessage(text=f'資料更新時間: {t}')]

            for info in parking_infos:
                if info.get('availablecar', 0) > 0:
                    area = info.get('area', '')
                    name = info.get('name', '')
                    car = info.get('availablecar', '')
                    msgs.append(LocationSendMessage(
                        title=f'{area} {name}  汽: {car}',
                        address=info['address'],
                        latitude=info['lat'],
                        longitude=info['lon'],
                    ))
            if len(msgs) == 1:
                raise ValueError('無停車場資訊')
        except Exception:
            raise ValueError('無停車場資訊')
    except Exception as e:
        msgs = [TextSendMessage(text=str(e))]
    line_bot_api.reply_message(event.reply_token, msgs[:5])


@scheduler.scheduled_job('cron', minute='*/1', second=0, id='update_data')
def update_data():
    global parking_df, parking_avail, df
    r = requests.get('https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json')
    parking_avail = r.json()
    available_df = pd.DataFrame(parking_avail['data']['park'])
    df = pd.merge(parking_df, available_df, how='right', left_on='id', right_on='id')


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


def start_schedule():
    scheduler.start()


if __name__ == '__main__':
    update_data()
    if STORAGE_FILE_NAME in os.listdir('./'):
        c_embedding = file.load()
    else:
        c_embedding = {}
        for idx, r in df.iterrows():
            txt = f"""
            {r['area']} {r['name'] } {r['summary']} {r['address']} {r['payex']}
            """
            c_embedding[idx] = model.embedding(txt, EMBEDDING_MODEL)
        file.save(c_embedding)
    t = threading.Thread(target=start_schedule)
    t.start()
    app.run(host='0.0.0.0', port=8080)
