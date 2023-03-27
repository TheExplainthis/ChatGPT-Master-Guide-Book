
import os
from threading import Thread

import discord
from dotenv import load_dotenv
from flask import Flask

from discordBot import DiscordClient, Sender

load_dotenv()
app = Flask('ChatGPT-Discord-Bot')


def run():
    client = DiscordClient()
    sender = Sender()

    @client.tree.command(name='chat', description='Echo your message')
    async def chat(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        echo = message
        await interaction.response.defer()
        await sender.send_message(interaction, message, echo)
    client.run(os.getenv('DISCORD_TOKEN'))


def server_run():
    app.run(host='0.0.0.0', port=5000)


@app.route('/')
def home():
    return "Hello World!"


if __name__ == '__main__':
    t = Thread(target=server_run)
    t.start()
    run()
