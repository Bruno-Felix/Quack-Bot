import discord
from discord.ext import commands
from random import randint

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

        if 'kaede' in (str(message.content).lower()) or 'kaebeça' in (str(message.content).lower()):
            await message.add_reaction('<:kaebeca:1234954376158773308>')

        if 'fleeky' in (str(message.content).lower()) or 'gang' == (str(message.content).lower()):
            await message.add_reaction('<:fleekabeca:1269741063946375188>')

        ## if 'r6' in (str(message.content).lower()):
        ##    await message.add_reaction('<:peepoEvil:914947766386581504>')

        if 'fifinha' in (str(message.content).lower()):
            await message.add_reaction('⚽')

            if "?" in (str(message.content).lower()):
                await message.add_reaction('❓')

# --------------

        if '!fifa' == (str(message.content).lower()):
            user_ids = [701955314161025086, 321389614940028929, 1028533279802011688, 406686196581007361, 358470646549839874]

            mentions = " ".join([f"<@{user_id}>" for user_id in user_ids])

            await message.channel.send(f'{mentions}')
            await message.channel.send(file=discord.File('static/fifa.gif'))

        if "!live" == (str(message.content).lower()):
            await message.channel.send(file=discord.File('static/tohrjob.gif'))


# --------------


async def setup(bot):
    await bot.add_cog(Message(bot))