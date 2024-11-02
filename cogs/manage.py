import discord

from discord import app_commands
from discord.ext import commands


class Manage(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="reload", description="reload cogs(for develop)")
    async def reload(self, interaction: discord.Interaction, extension_name: str):
        if str(interaction.user.id) != str(self.bot.owner_id):
            await interaction.response.send_message("Only bot owner can use this command!", ephemeral=True)
            return
        try:
            await self.bot.reload_extension(f"cogs.{extension_name}")
            await self.bot.tree.sync()
            await interaction.response.send_message(f"successful reload {extension_name}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"reload {extension_name} failed\nerror: {e}", ephemeral=True)

    @app_commands.command(name="unload", description="unload cogs(for develop)")
    async def unload(self, interaction: discord.Interaction, extension_name: str):
        if str(interaction.user.id) != str(self.bot.owner_id):
            await interaction.response.send_message("Only bot owner can use this command!", ephemeral=True)
            return
        try:
            await self.bot.load_extension(f"cogs.{extension_name}")
            await self.bot.tree.sync()
            await interaction.response.send_message(f"successful unload {extension_name}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"unload {extension_name} failed\nerror: {e}", ephemeral=True)

    @app_commands.command(name="load", description="load cogs(for develop)")
    async def load(self, interaction: discord.Interaction, extension_name: str):
        if str(interaction.user.id) != str(self.bot.owner_id):
            await interaction.response.send_message("Only bot owner can use this command!", ephemeral=True)
            return
        try:
            await self.bot.load_extension(f"cogs.{extension_name}")
            await self.bot.tree.sync()
            await interaction.response.send_message(f"successful load {extension_name}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"load {extension_name} failed\nerror: {e}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Manage(bot), guild=None)
