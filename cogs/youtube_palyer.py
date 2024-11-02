import discord
import os
import yt_dlp

from discord import app_commands
from discord.ext import commands


class YotubePlayer(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = ['/', '\\', ':',
                               '*', '?', '"', '\'', '<', '>', '|']
        self.play_queue = []
        self.pause_flag = False
        self.ffmpeg_path = './ffmpeg/bin/ffmpeg.exe'
        self.song_path = './music_tmp/'
        self.cookie_path = './cookies.txt'
        self.volume = 0.1

    @app_commands.command(name='join', description='加入語音頻道')
    async def join(self, interaction: discord.Interaction) -> None:
        if interaction.user.voice == None:
            await interaction.response.send_message('未加入頻道')
        elif len(self.bot.voice_clients) == 0:
            voiceChannel = interaction.user.voice.channel
            await voiceChannel.connect()
            await self.change_status(discord.Activity(
                type=discord.ActivityType.listening, name='Youtube'))
        else:
            await interaction.response.send_message('已加入頻道')

    @app_commands.command(name="leave", description="離開語音頻道")
    async def leave(self, interaction: discord.Interaction) -> None:
        if len(self.bot.voice_clients) != 0:
            await self.bot.voice_clients[0].disconnect()
            self.play_queue = []
            await self.change_status(discord.Activity(
                type=discord.ActivityType.watching, name='ご注文はうさぎですか？'))
            await interaction.response.send_message("已離開頻道~")
        else:
            await interaction.response.send_message("目前沒有在任何頻道!")
        self.clean(self)

    async def change_status(self, state) -> None:
        await self.bot.change_presence(activity=state, status=discord.Status.online)

    def clean(self):
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == ".mp3":
                    os.remove(file.path)
        except PermissionError:
            print("file is open now!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YotubePlayer(bot), guild=None)
