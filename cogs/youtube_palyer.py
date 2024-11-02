import discord
import os
import yt_dlp

from discord import app_commands
from discord.ext import commands
from loguru import logger

from src.tools import error_output


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
        if await self.handle_connect(interaction):
            await interaction.response.send_message('已加入頻道')
        else:
            await interaction.response.send_message('未加入頻道')

    @app_commands.command(name='leave', description='離開語音頻道')
    async def leave(self, interaction: discord.Interaction) -> None:
        if len(self.bot.voice_clients) != 0:
            await self.bot.voice_clients[0].disconnect()
            self.play_queue = []
            await self.change_status(discord.Activity(
                type=discord.ActivityType.watching, name='ご注文はうさぎですか？'))
            await interaction.response.send_message('已離開頻道~')
        else:
            await interaction.response.send_message('目前沒有在任何頻道!')
        self.clean(self)

    @app_commands.command(name='play', description='播放YT音樂')
    async def play(self, interaction: discord.Interaction, youtube_url: str) -> None:
        await interaction.response.defer()
        youtube_url = self.url_format(youtube_url)
        if youtube_url == None:
            await interaction.followup.send(f'找不到歌曲呦!')
            return
        if await self.handle_connect(interaction):
            try:
                await self.get_details(youtube_url)
            except Exception as e:
                logger.error(e)
                embed = await error_output(e)
                await interaction.followup.send(embed=embed)
                return
            if not self.bot.voice_clients[0].is_playing():
                await interaction.followup.send(f'歌單已加入: 歌單URL為{youtube_url} 呦🌟 即將開始播放歌曲~')
                title = self.play_queue[0]['title']
                url = self.play_queue[0]['url']
                ydl_opts = {
                    'cookiefile': self.cookie_path,
                    'format': 'bestaudio/best',
                    'outtmpl': f'{self.song_path}{title}',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                except:
                    for f in self.forbidden_char:
                        title = title.replace(f, ' ')
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                # self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=f'{
                #                                self.song_path}{title}.mp3'), volume=self.volume), after=lambda _: self.after_song_interface(interaction))
            else:
                await interaction.followup.send(f'歌曲已加入排序: 歌單URL為{youtube_url} 呦🌟')
        else:
            await interaction.followup.send('未加入頻道')

    async def get_details(self, youtube_url: str) -> None:
        ydl_opts = {
            'cookiefile': self.cookie_path,
            'extract_flat': True,  # dont download
            'quiet': True,  # undisplay progress bar
            'noplaylist': False,  # playlist
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            details = ydl.extract_info(youtube_url, download=False)
            if details.get('entries') == None:  # check if not a playlist
                song_details = [
                    {'url': youtube_url, 'title': details.get('title')}]
            else:
                song_details = [entry for entry in details.get(
                    'entries') if entry.get('title') not in {'[Deleted video]', '[Private video]'}]
            logger.info(str(
                [map(lambda x: {'url': x.get('url'), 'title': x.get('title')}, song_details)]))
            self.play_queue.extend(song_details)

    def url_format(self, youtube_url: str) -> str | None:
        if '&list=' in youtube_url:
            youtube_url = youtube_url[0:youtube_url.find('&list=')]

        if youtube_url.startswith('https://www.youtube.com/'):
            return youtube_url
        elif youtube_url.startswith('https://music.youtube.com/'):
            return youtube_url.replace('music', 'www')
        elif youtube_url.startswith('https://youtube.com/'):
            return youtube_url.replace('https://youtube', 'https://www.youtube')
        else:
            return None

    async def handle_connect(self, interaction: discord.Interaction) -> bool:
        if interaction.user.voice == None:
            return False
        elif len(self.bot.voice_clients) == 0:
            await interaction.user.voice.channel.connect()
            await self.change_status(discord.Activity(
                type=discord.ActivityType.listening, name='Youtube'))
            return True
        else:
            return True

    async def change_status(self, state) -> None:
        await self.bot.change_presence(activity=state, status=discord.Status.online)

    def clean(self):
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == '.mp3':
                    os.remove(file.path)
        except PermissionError:
            logger.error('file is open!')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YotubePlayer(bot), guild=None)
