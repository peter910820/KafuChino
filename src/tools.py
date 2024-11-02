import discord


async def error_output(error_message):
    embed = discord.Embed(
        title='ERROR', description='An error has occurred', color=discord.Color.red())
    embed.add_field(name='Error content', value=error_message)
    return embed


async def youtube_palyer_output(youtube_palyer_message):
    embed = discord.Embed(
        title='YT-PLAYER', description='youtube_palyer message', color=discord.Color.dark_red())
    embed.add_field(name='Notice', value=youtube_palyer_message)
    return embed
