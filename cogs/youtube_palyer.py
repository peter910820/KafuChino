import discord
import os
import re
import yt_dlp

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

from src.tools import error_output, youtube_palyer_output

load_dotenv()


class YotubePlayer(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = re.compile(r'[/\\:*?"\'<>|]')
        self.play_queue = []
        self.pause_flag = False
        self.ffmpeg_path = os.getenv('FFMPEG_PATH')
        self.song_path = './music_tmp/'
        self.cookie_path = './cookies.txt'
        self.volume = 0.1
        self.get_details_options = {
            'cookiefile': self.cookie_path,
            'extract_flat': True,  # dont download
            'quiet': True,  # undisplay progress bar
            'noplaylist': False,  # playlist
        }
        self.ydl_opts_postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]

    @app_commands.command(name='join', description='加入語音頻道')
    async def join(self, interaction: discord.Interaction) -> None:
        if await self.handle_connect(interaction, 'join'):
            await interaction.response.send_message(embed=await youtube_palyer_output('已加入頻道'))
        else:
            await interaction.response.send_message(embed=await youtube_palyer_output('加入頻道失敗，請確保使用者在語音頻道內且機器人不在其他語音頻道'))

    @app_commands.command(name='leave', description='離開語音頻道')
    async def leave(self, interaction: discord.Interaction) -> None:
        if await self.handle_connect(interaction, 'leave'):
            await interaction.response.send_message(embed=await youtube_palyer_output('離開語音頻道成功'))
        else:
            await interaction.response.send_message(embed=await youtube_palyer_output('機器人未加入頻道'))

    @app_commands.command(name='play', description='播放YT音樂')
    async def play(self, interaction: discord.Interaction, youtube_url: str) -> None:
        await interaction.response.defer()
        youtube_url = self.url_format(youtube_url)
        if youtube_url == None:
            await interaction.followup.send(embed=await youtube_palyer_output('找不到歌曲喔'))
            return
        if await self.handle_connect(interaction, 'play'):
            try:
                await self.get_details(youtube_url)
            except Exception as e:
                logger.error(e)
                embed = await error_output(e)
                await interaction.followup.send(embed=embed)
                return
            if not self.bot.voice_clients[0].is_playing():
                await interaction.followup.send(embed=await youtube_palyer_output(f'歌曲/單已加入: 加入網址為{youtube_url} 即將開始播放歌曲~'))
                title = self.forbidden_char.sub(
                    '_', self.play_queue[0]['title'])
                url = self.play_queue[0]['url']
                music_path = f'{self.song_path}{title}'
                ydl_opts = {
                    'cookiefile': self.cookie_path,
                    'format': 'bestaudio/best',
                    'outtmpl': music_path,
                    'postprocessors': self.ydl_opts_postprocessors,
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                except Exception as e:
                    logger.error(e)
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                    executable=self.ffmpeg_path, source=f'{music_path}.mp3'), volume=self.volume)
                self.bot.voice_clients[0].play(
                    source, after=lambda _: self.after_song_interface(interaction))
            else:
                await interaction.followup.send(f'歌曲已加入排序: 歌單URL為{youtube_url}')
        else:
            await interaction.followup.send('未加入頻道')

    def after_song_interface(self, interaction: discord.Interaction):
        self.bot.loop.create_task(self.after_song(interaction))

    async def after_song(self, interaction: discord.Interaction):
        self.play_queue.pop(0)
        self.clean(self)
        if len(self.play_queue) > 0:
            title = self.forbidden_char.sub('_', self.play_queue[0]['title'])
            url = self.play_queue[0]['url']
            music_path = f'{self.song_path}{title}'
            ydl_opts = {
                'cookiefile': self.cookie_path,
                'format': 'bestaudio/best',
                'outtmpl': music_path,
                'postprocessors': self.ydl_opts_postprocessors,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                logger.error(e)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                executable=self.ffmpeg_path, source=f'{music_path}.mp3'), volume=self.volume)
            self.bot.voice_clients[0].play(
                source, after=lambda _: self.after_song_interface(interaction))
        else:
            self.clean(self)
            await self.change_status(discord.Activity(
                type=discord.ActivityType.watching, name='ご注文はうさぎですか？'))
            logger.success('已播放完歌曲')
            await interaction.followup.send(embed=await youtube_palyer_output('已播放完歌曲'))

    @app_commands.command(name='skip', description='跳過歌曲')
    async def skip(self, interaction: discord.Interaction, count: int = 1) -> None:
        await interaction.response.defer()
        if len(self.play_queue) != 0:
            self.bot.voice_clients[0].stop()
        else:
            await interaction.followup.send('我還沒加入語音頻道呦')
            return
        if count > 1:
            if count > len(self.play_queue):
                count = len(self.play_queue)
            count -= 1
            for _ in range(0, count):
                self.play_queue.pop(0)
        await interaction.followup.send(embed=await youtube_palyer_output('歌曲已跳過'))

    @app_commands.command(name='pause', description='暫停歌曲')
    async def pause(self, interaction) -> None:
        if self.bot.voice_clients[0].is_playing():
            self.bot.voice_clients[0].pause()
            self.pause_flag = True
            await interaction.response.send_message(embed=await youtube_palyer_output('歌曲已暫停'))
        else:
            await interaction.response.send_message(embed=await youtube_palyer_output('沒有歌曲正在播放'))

    @app_commands.command(name='resume', description='回復播放歌曲')
    async def resume(self, interaction) -> None:
        if self.bot.voice_clients[0].is_paused():
            self.bot.voice_clients[0].resume()
            self.pause_flag = False
            await interaction.response.send_message(embed=await youtube_palyer_output('歌曲已繼續播放'))
        else:
            await interaction.response.send_message(embed=await youtube_palyer_output('沒有歌曲正在暫停'))

    @app_commands.command(name='insert', description='插入歌曲到下一首')
    async def insert(self, interaction: discord.Interaction, youtube_url: str) -> None:
        await interaction.response.defer()
        youtube_url = self.url_format(youtube_url)
        if youtube_url.startswith('https://www.youtube.com/playlist?list='):
            await interaction.followup.send(embed=await youtube_palyer_output('此功能不支援清單插入呦'))
            return
        elif not youtube_url.startswith('https://www.youtube.com/'):
            await interaction.followup.send(embed=await youtube_palyer_output('找不到歌曲呦'))
        else:
            if await self.handle_connect(interaction, 'insert'):
                await interaction.followup.send(embed=await youtube_palyer_output('插入歌曲到下一首'))
                try:
                    with yt_dlp.YoutubeDL(self.get_details_options) as ydl:
                        details = ydl.extract_info(youtube_url, download=False)
                        if details.get('entries') == None:  # check if not a playlist
                            self.play_queue.insert(1, {details})
                        logger.info(self.play_queue[1])
                except Exception as e:
                    logger.error(e)
            else:
                await interaction.followup.send(embed=await youtube_palyer_output('機器人未加入頻道'))

    @app_commands.command(name='list', description='查詢歌曲清單')
    async def list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        if len(self.play_queue) == 0:
            await interaction.followup.send(embed=await youtube_palyer_output('播放清單目前為空呦'))
        else:
            display = f'播放清單剩餘歌曲: {len(self.play_queue)}首\n :arrow_forward: '
            for index, t in enumerate(self.play_queue, start=1):
                display += f'{index}. {t["title"]}\n'
                if len(display) >= 500:
                    display += ' ...還有很多首'
                    break
            logger.info(display)
            await interaction.followup.send(embed=await youtube_palyer_output(display))

    async def get_details(self, youtube_url: str) -> None:
        with yt_dlp.YoutubeDL(self.get_details_options) as ydl:
            details = ydl.extract_info(youtube_url, download=False)
            if details.get('entries') == None:  # check if not a playlist
                song_details = [
                    {'url': youtube_url, 'title': details.get('title')}]
            else:
                song_details = [entry for entry in details.get(
                    'entries') if entry.get('title') not in {'[Deleted video]', '[Private video]'}]
            logger.info(str(list(
                map(lambda x: {'url': x.get('url'), 'title': x.get('title')}, song_details))))
            self.play_queue.extend(song_details)

    def url_format(self, youtube_url: str) -> str | None:
        if youtube_url.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/')):
            return youtube_url
        elif youtube_url.startswith('https://music.youtube.com/'):
            return youtube_url.replace('music', 'www')
        else:
            return None

    async def handle_connect(self, interaction: discord.Interaction, command: str) -> bool:
        match command:
            case 'join':
                if len(self.bot.voice_clients) == 0:
                    if interaction.user.voice != None:
                        await interaction.user.voice.channel.connect()
                        await self.change_status(discord.Activity(
                            type=discord.ActivityType.listening, name='Youtube'))
                        return True
                    return False
                else:
                    return False
            case 'leave':
                if len(self.bot.voice_clients) != 0:
                    await self.bot.voice_clients[0].disconnect()
                    self.play_queue = []
                    self.clean(self)
                    await self.change_status(discord.Activity(
                        type=discord.ActivityType.watching, name='ご注文はうさぎですか？'))
                    return True
                else:
                    return False
            case 'play' | 'insert':
                return True if len(self.bot.voice_clients) != 0 else False
            case _:
                logger.critical("A unknown error has occurred!")

    async def change_status(self, state) -> None:
        await self.bot.change_presence(activity=state, status=discord.Status.online)

    def clean(self, _: discord.Interaction):
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == '.mp3':
                    os.remove(file.path)
        except PermissionError:
            logger.error('file is open!')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YotubePlayer(bot), guild=None)
