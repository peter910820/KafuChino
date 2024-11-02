import discord


async def error_output(error_message):
    embed = discord.Embed(
        title='ERROR', description='An error has occurred', color=discord.colour.Colour.magenta())
    embed.add_field(name='Error content', value=error_message)
    return embed


async def notice_output(youtube_palyer_message):
    embed = discord.Embed(
        title='YT-PLAYER', description='youtube_palyer message', color=discord.colour.Colour.blurple())
    embed.add_field(name='Notice', value=youtube_palyer_message)
    return embed
