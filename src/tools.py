import discord


async def error_output(error_message):
    embed = discord.Embed(
        title='ERROR', description='An error has occurred', color=discord.Color.red())
    embed.add_field(name='Error content', value=error_message)
    return embed
