
import os
from threading import Thread

import discord
from dotenv import load_dotenv
from flask import Flask
from models import OpenAIModel
from memory import Memory

from discordBot import DiscordClient, Sender

load_dotenv()
app = Flask('ChatGPT-Discord-Bot')


model = OpenAIModel(api_key=os.getenv('OPENAI_API_TOKEN'), model_engine=os.getenv('OPENAI_MODEL_ENGINE'))
memory = Memory(system_message=os.getenv('OPENAI_SYSTEM_MESSAGE'), memory_message_count=2)


def run():
    client = DiscordClient()
    sender = Sender()

    @client.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        user_id = interaction.user.id
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        prompt = os.getenv('PROMPT').format(message)
        memory.append(user_id, {'role': 'user', 'content': prompt})
        is_successful, response = model.chat_completion(memory.get(user_id))
        if is_successful:
            role = response['choices'][0]['message']['role']
            content = response['choices'][0]['message']['content'].strip()
            memory.append(user_id, {'role': role, 'content': content})
        else:
            content = response
            memory.remove(user_id)
        await sender.send_message(interaction, message, content)

    @client.tree.command(name="reset", description="Reset ChatGPT conversation history")
    async def reset(interaction: discord.Interaction):
        user_id = interaction.user.id
        try:
            memory.remove(user_id)
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f'> Reset ChatGPT conversation history < - <@{user_id}>')
        except Exception:
            await interaction.followup.send('> Oops! Something went wrong. <')

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
