import discord

intents = discord.Intents.default()
intents.message_content = True


class DiscordClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.synced = False
        self.added = False
        self.tree = discord.app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/chat")

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        if not self.added:
            self.added = True


class Sender():
    async def send_message(self, interaction, receive, response):
        try:
            user_id = interaction.user.id
            result = f'> **{receive}** - <@{str(user_id)}> \n\n{response}'
            await interaction.followup.send(result)
        except Exception:
            await interaction.followup.send('> **Error: Something went wrong, please try again later!**')
