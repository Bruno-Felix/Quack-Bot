import discord, os
from dotenv import load_dotenv
from discord.ext import commands
from random import randint

from static.roles import rules
from static.triples_colors import get_sort_triples_color

from src.mentions import get_users_by_reaction
from static.reactions import reactions

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


        if "!live" == (str(message.content).lower()):
            await message.channel.send(file=discord.File('static/tohrjob.gif'))

        for reaction in reactions:
            if f"!{reaction['command']}" == (str(message.content).lower()):
                mentions = await get_users_by_reaction(self, JOGOS_CHANNEL_ID,
                                                       JOGOS_REACTIONS_MESSAGE_ID, reaction['emoji'])

                if mentions:
                    await message.channel.send(f'{mentions}')
                    if 'gif' in reaction:
                       await message.channel.send(file=discord.File(reaction['gif'])) 
                else:
                    await message.channel.send(f"Ninguém reagiu para {reaction['description']}")

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

    @commands.command(name="reagir")
    async def reagir_msg(self, ctx):
        embed = discord.Embed(
            title='Escolha os jogos que queira ser notificado!!',
            description='Reaja a esta mensagem com o emoji do respectivo jogo para lhe mencionar na proxima jogatina:',
            color=get_sort_triples_color()
        )

        for reaction in reactions:
            embed.add_field(name=f"{reaction['emoji']}", value=f"{reaction['description']}", inline=True)

        msg = await ctx.send(embed=embed)

        for reaction in reactions:
            await msg.add_reaction(reaction['emoji'])


# --------------


async def setup(bot):
    await bot.add_cog(Message(bot))
