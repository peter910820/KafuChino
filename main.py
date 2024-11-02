import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True


class KafuChino(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='$',
            intents=intents,
            owner_id=os.getenv('BOT_OWNER')
        )

    async def setup_hook(self):
        # This feature to slash command has an error
        # await self.load_extension('cogs.manage')
        await self.load_extension('cogs.general')
        await bot.tree.sync(guild=None)

    async def on_ready(self):
        delay_time = str(round(self.latency*1000, 2))
        logger.success(f'{self.user} is starting......')
        logger.success(f'{self.user} is online. delay time: {delay_time}ms.')
        status = discord.Activity(
            type=discord.ActivityType.watching, name='ご注文はうさぎですか？')
        await self.change_presence(status=discord.Status.online, activity=status)


bot = KafuChino()
bot.run(os.getenv('BOT_TOKEN'))
