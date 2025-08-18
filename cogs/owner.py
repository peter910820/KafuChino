import discord

from discord import app_commands
from discord.ext import commands
from loguru import logger

from src.tools import error_output, owner_output


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != str(self.bot.owner_id):
            await interaction.response.send_message(embed=await owner_output('Only bot owner can use this command!'), ephemeral=True)
            return False
        return True

    @app_commands.command(name='close', description='close bot(owner only)')
    async def close(self, interaction: discord.Interaction):
        if not await self.check_owner(interaction):
            return
        try:
            logger.info('正在關閉機器人...')
            await interaction.response.send_message(embed=await owner_output('正在關閉機器人...'), ephemeral=True)
            await self.bot.close()
        except Exception as e:
            logger.error(e)
            await interaction.response.send_message(embed=await error_output(e))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot), guild=None)
