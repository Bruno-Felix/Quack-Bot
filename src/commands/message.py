import discord
from discord.ext import commands
from random import randint

from static.roles import rules
from static.triples_colors import get_sort_triples_color

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
            gif_number = randint(1, 2)

            await message.channel.send('QUACK Yeonji mencionada!!')
            await message.channel.send(file=discord.File(f'static/quack_{gif_number}.gif'))

        if 'maluca' in (str(message.content).lower()):
            gif_number = randint(1, 5)

            await message.channel.send('MALUCA mencionada!!')
            await message.channel.send(file=discord.File(f'static/chaeyeon_{gif_number}.gif'))

        if 'medica' in (str(message.content).lower()) or 'médica' in (str(message.content).lower()):
            gif_number = randint(1, 5)

            await message.channel.send('MEDICA mencionada!!')
            await message.channel.send(file=discord.File(f'static/medica{gif_number}.gif'))


# --------------


        if '!fifa' == (str(message.content).lower()):
            user_ids = [321389614940028929, 406686196581007361, 358470646549839874, 182935000046370816, 183630868114309120]

            mentions = " ".join([f"<@{user_id}>" for user_id in user_ids])

            await message.channel.send(f'{mentions}')
            await message.channel.send(file=discord.File('static/fifa.gif'))

        if "!live" == (str(message.content).lower()):
            await message.channel.send(file=discord.File('static/tohrjob.gif'))

        if message.content.lower().startswith('!regra'):
            try:
                embed = discord.Embed(
                    color=get_sort_triples_color()
                )

                role_number = int(message.content[6:])
                rule = rules[role_number - 1]
                
                embed.add_field(name=rule['title'], value=rule['body'], inline=False)
                
                await message.channel.send(embed=embed)
            except:
                None


# --------------


async def setup(bot):
    await bot.add_cog(Message(bot))
