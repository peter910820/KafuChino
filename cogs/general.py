import discord

from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='ping', description='return bot delay')
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'delay time: {str(round(self.bot.latency*1000, 2))}ms.')

    @app_commands.command(name='id', description='check user id.')
    async def id(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Your user ID: {interaction.user.id}')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot), guild=None)