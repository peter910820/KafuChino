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
            await self.change_status_music(discord.Activity(
                type=discord.ActivityType.listening, name="Youtube"))
        else:
            await interaction.response.send_message('已加入頻道')

    async def change_status(self, state) -> None:
        await self.bot.change_presence(activity=state, status=discord.Status.online)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YotubePlayer(bot), guild=None)
