import discord

from discord import app_commands
from discord.ext import commands


class Manage(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='cog', description='Manage cogs(for develop)')
    @app_commands.describe(action_name='The action to manage cog.')
    @app_commands.choices(action_name=[
        app_commands.Choice(name='load', value='load'),
        app_commands.Choice(name='unload', value='unload'),
        app_commands.Choice(name='reload', value='reload'),
    ])
    async def reload(self, interaction: discord.Interaction, action_name: str, extension_name: str):
        if str(interaction.user.id) != str(self.bot.owner_id):
            await interaction.response.send_message('Only bot owner can use this command!', ephemeral=True)
            return
        try:
            match action_name:
                case 'load':
                    await self.bot.load_extension(f'cogs.{extension_name}')
                case 'unload':
                    await self.bot.unload_extension(f'cogs.{extension_name}')
                case 'reload':
                    await self.bot.reload_extension(f'cogs.{extension_name}')
            await self.bot.tree.sync()
            print(f'successful {action_name} {extension_name}')
        except Exception as e:
            print(f'{action_name} {extension_name} failed\nerror: {e}')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Manage(bot), guild=None)
