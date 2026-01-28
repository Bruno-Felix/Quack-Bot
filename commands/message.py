import discord, os
from dotenv import load_dotenv
from discord.ext import commands
from random import randint

from static.triples_colors import get_sort_triples_color

from src.mentions import get_users_by_reaction

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

JOGOS_CHANNEL_ID = os.getenv('JOGOS_CHANNEL_ID')
JOGOS_REACTIONS_MESSAGE_ID = os.getenv('JOGOS_REACTIONS_MESSAGE_ID')

class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.embeds or message.attachments:
            return
        
        if '/malu' == str(message.content).lower():
            await message.channel.send(file=discord.File(f'static/malu_gowon.gif'))
        
        if 'quack' in (str(message.content).lower()):
            await message.add_reaction('<:joia:1374114967418048573>')

        if 'maluca' in (str(message.content).lower()):
            await message.add_reaction('<:joia:1374114967418048573>')

        if 'kaede' in (str(message.content).lower()):
            await message.add_reaction('<:kaedeca:1374079658953281536>')

        if 'fran' in (str(message.content).lower()):
            await message.add_reaction('<:sapinhodansa:1377317641760407583>')

        if 'medica' in (str(message.content).lower()) or 'médica' in (str(message.content).lower()):
            await message.add_reaction('<:joia:1374114967418048573>')

        if 'cafe' in (str(message.content).lower()) or 'café' in (str(message.content).lower()):
            await message.add_reaction('<:gatojoia:1374091388010106923>')

        if 'chuu' in (str(message.content).lower()):
            await message.add_reaction('<:chuu:1374091856874307584>')


async def setup(bot):
    await bot.add_cog(Message(bot))
