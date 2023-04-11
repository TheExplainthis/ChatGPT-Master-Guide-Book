
import os
from threading import Thread

import discord
from dotenv import load_dotenv
from flask import Flask
import opencc

from models import OpenAIModel
from discordBot import DiscordClient, Sender


load_dotenv()
app = Flask('ChatGPT-Discord-Bot')

s2t_converter = opencc.OpenCC('s2t')
model = OpenAIModel(api_key=os.getenv('OPENAI_API_KEY'))
CHAT_MODEL = os.getenv('CHAT_COMPLETION_MODEL', 'gpt-3.5-turbo')


def run():
    client = DiscordClient()
    sender = Sender()

    @client.tree.command(name='brainstorming', description='ChatGPT help you brainstorm and come up with ten ideas.')
    async def brainstorming(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        try:
            messages = [{
                'role': 'system',
                'content': '你現在是一個很會做創意發想的人，能夠想到各式各樣的點子'
            }, {
                'role': 'user',
                'content': f'請提供 10 個關於 """如何 {message} """ 的各種方法、想法、作法、點子'
            }]
            _, content = model.chat_completion(messages, CHAT_MODEL)
            content = s2t_converter.convert(content)
            await sender.send_message(interaction, message, content)
        except Exception as e:
            await sender.send_message(interaction, message, str(e))

    @client.tree.command(name='translate', description='ChatGPT help you translate English into Chinese.')
    async def translate(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        await interaction.response.defer()

        try:
            messages = [{
                'role': 'system',
                'content': '你現在精通中英文，非常擅長將英文翻譯成中文'
            }, {
                'role': 'user',
                'content': f'將 """{message}""" 翻譯成中文'
            }]
            _, content = model.chat_completion(messages, CHAT_MODEL)
            content = s2t_converter.convert(content)
            await sender.send_message(interaction, message, content)
        except Exception as e:
            await sender.send_message(interaction, message, str(e))
    client.run(os.getenv('DISCORD_TOKEN'))


def server_run():
    app.run(host='0.0.0.0', port=5000)


@app.route('/')
def home():
    return 'Hello World!'


if __name__ == '__main__':
    t = Thread(target=server_run)
    t.start()
    run()
