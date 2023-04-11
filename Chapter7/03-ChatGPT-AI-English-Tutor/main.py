from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, AudioMessage, AudioSendMessage

from audio import audio
from models import OpenAIModel
from speech import Speech

import math
import os
import uuid
load_dotenv()


app = Flask(__name__, static_url_path='/audio', static_folder='files/')

model = OpenAIModel(os.getenv('OPENAI_API_KEY'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

speech = Speech()

CHAT_MODEL = os.getenv('CHAT_COMPLETION_MODEL', 'gpt-3.5-turbo')
AUDIO_MODEL = os.getenv('AUDIO_MODEL_ENGINE', 'whisper-1')
SERVER_URL = os.getenv('SERVER_URL', None)


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


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    audio_content = line_bot_api.get_message_content(event.message.id)
    input_audio_path = f'{str(uuid.uuid4())}.m4a'
    with open(input_audio_path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    text = model.audio_transcriptions(input_audio_path, 'whisper-1')

    messages = [{
        'role': 'system',
        'content': '你現在是生活在美國的英文老師，你知道如何糾正學生的錯誤文法、並且知道如何引導學生進步，是他們英文更好'
    }, {
        'role': 'user',
        'content': f'學生說："""{text}""" \n\n 如果他文法有誤請糾正他，並可以延伸他的句子。如果他是問題，請回應他，回覆盡量具體，有方法。請直接給他英文回覆，不需要禮貌、不需要重複他的問題'
    }]

    _, content = model.chat_completion(messages, CHAT_MODEL)

    output_audio_path = f'{str(uuid.uuid4())}.mp3'

    speech.text_to_speech(content, 'en-US-Studio-O', 'en-US', output_audio_path)

    audio_name = f'{str(uuid.uuid4())}.m4a'
    response_audio_path = f'files/{audio_name}'
    audio.convert_to_aac(output_audio_path, response_audio_path)
    duration = audio.get_audio_duration(output_audio_path)
    audio_url = f'{SERVER_URL}/audio/{audio_name}'

    if input_audio_path in os.listdir('./'):
        os.remove(input_audio_path)
    if output_audio_path in os.listdir('./'):
        os.remove(output_audio_path)

    line_bot_api.reply_message(
        event.reply_token,
        [
            AudioSendMessage(original_content_url=audio_url, duration=math.ceil(duration*1000)),
            TextSendMessage(text=content)
        ]
    )


@app.route("/", methods=['GET'])
def home():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
