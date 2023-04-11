from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage

from lineComponent import line_component
from models import OpenAIModel
from service import GoogleMap
from utils import construct_sections

from ast import literal_eval
import os
load_dotenv()


app = Flask(__name__, static_url_path='/image', static_folder='photos/')

models = OpenAIModel(os.getenv('OPENAI_API_KEY'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
google_map_api = GoogleMap(os.getenv('GOOGLE_MAP_API_KEY'))
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
        msgs = [{
            'role': 'system',
            'content': '你能夠從一串敘述中有條理的組織資訊'
        }, {
            'role': 'user',
            'content': f"""
            用戶會給一段 Google Map 的輸入字串，如下：{query}

            評論人數最多不超過 10000, 最少不低於 0
            評論分數最高不超過 5，最低不低於 0

            請給我一個 Object，回傳相對應的欄位：
            {{
            "名詞關鍵字": "...",
            "形容詞關鍵字": "...",
            "評論人數": "(最少人數, 最多人數)",
            "評論分數": "(最低分數, 最高分數)",
            }}

            其他什麼都不要說，回傳一個 Object 就好，return object, return {{}}
            """
        }]

        _, content = models.chat_completion(msgs, CHAT_MODEL)
        try:
            data = literal_eval(content)
        except Exception:
            raise ValueError('請給更多條件，例：評論數、評分')

        noun_keyords = data.get('名詞關鍵字')
        if type(noun_keyords) == list:
            noun_keyords = ' '.join(noun_keyords)
        if len(noun_keyords) == 0:
            raise ValueError('沒有偵測到名詞地標，請重新輸入')

        adj_keywords = data.get('形容詞關鍵字')
        if type(adj_keywords) == list:
            adj_keywords = ' '.join(adj_keywords)

        places = google_map_api.get_places(noun_keyords)
        selected_places = []
        for place in places:
            raw_count = data.get('評論人數', [0, 10000])
            raw_rating = data.get('評論分數', [0, 5])
            count = literal_eval(raw_count)
            rating = literal_eval(raw_rating)
            rating_total = place['user_ratings_total']
            if rating_total < count[0] or \
               rating_total > count[1]:
                continue
            if place['rating'] < rating[0] or \
               place['rating'] > rating[1]:
                continue
            selected_places.append(place)
        if len(selected_places) == 0:
            raise ValueError('找不到任何地點，請重新輸入')

        for place in selected_places:
            place_id = place['place_id']
            details = google_map_api.get_details(place_id)
            place.update(details)

        txt = construct_sections(selected_places)
        messages = [{
            'role': 'system',
            'content': '你能夠從眾多資訊中，推薦適合我的品項'
        }, {
            'role': 'user',
            'content': f"""
            店家資訊為：{txt}
            請針對我的需求：{noun_keyords} {adj_keywords}
            推薦我三個物件

            回傳格式如下：['place_id', 'place_id', '...']
            其他什麼都不要說，回傳一個 array 就好
            return array
            """
        }]
        _, content = models.chat_completion(messages, CHAT_MODEL)
        try:
            places_id = literal_eval(content)
        except Exception:
            raise ValueError(content)
        filter_places = []
        for place in selected_places:
            if place['place_id'] in places_id:
                filter_places.append(place)
        i_places = filter_places[:12]
        contents = line_component.get_contents(i_places)
        msg = FlexSendMessage(alt_text='result', contents=contents)
        line_bot_api.reply_message(event.reply_token, msg)
    except Exception as e:
        msg = TextSendMessage(text=str(e))
        line_bot_api.reply_message(event.reply_token, msg)


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
