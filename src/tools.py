import discord


async def error_output(error_message):
    embed = discord.Embed(
        title='ERROR', description='An error has occurred', color=discord.colour.Colour.magenta())
    embed.add_field(name='Error content', value=error_message)
    return embed


async def youtube_palyer_output(youtube_palyer_message):
    embed = discord.Embed(
        title='YT-PLAYER', description='youtube_palyer message', color=discord.colour.Colour.red())
    embed.add_field(name='Notice', value=youtube_palyer_message)
    return embed


async def general_output(general_message):
    embed = discord.Embed(
        title='Helper', description='Assistant for delivering messages', color=discord.colour.Colour.blue())
    embed.add_field(name='Notice', value=general_message)
    return embed


async def owner_output(owner_message):
    embed = discord.Embed(
        title='FOR-OWNER', description=owner_message, color=discord.colour.Colour.purple())
    return embed
