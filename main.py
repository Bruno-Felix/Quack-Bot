import os
from os.path import join, dirname
import discord
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

from functions import buscar_objekts, gerar_have_carteira, gerar_lista_links_carteiras, gerar_lista_links_objekts
from response import criar_resposta_discord

from data import dict_comandos_integrantes, dict_carteira_comandos

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content == '!links':
            await message.channel.send('QUACK! Silêncio, Quack Yeonji está trabalhando...')
            
            try:
                resposta = criar_resposta_discord(gerar_lista_links_objekts())

                await message.channel.send('QUACK! Lista de Links importantes para trade e objekts:\n')
                await message.channel.send(resposta)
            except Exception as error:
                await message.channel.send('QUACK! houve algum problema, tente novamente mais tarde.')
                print(error)

        
        if message.content == '!carteiras':
            await message.channel.send('QUACK! Silêncio, Quack Yeonji está trabalhando...')

            try:
                resposta = criar_resposta_discord(gerar_lista_links_carteiras())

                await message.channel.send('QUACK! Lista dos links das carteiras do Xet:\n')
                await message.channel.send(resposta)
            except Exception as error:
                await message.channel.send('QUACK! houve algum problema, tente novamente mais tarde.')
                print(error)

        integrante = None
        pessoa = None

        try:
            integrante = dict_comandos_integrantes[message.content]
        except Exception:
            pass

        try:
            pessoa = dict_carteira_comandos[message.content]
        except Exception:
            pass

        if integrante:
            await message.channel.send('QUACK! Silêncio, Quack Yeonji está trabalhando...')

            try:
                resposta = criar_resposta_discord(buscar_objekts(integrante))
            
                await message.channel.send(resposta)
            except Exception as error:
                await message.channel.send('QUACK! houve algum problema, tente novamente mais tarde.')
                print(error)

        if pessoa:
            await message.channel.send('QUACK!')
            
            try:
                resposta = criar_resposta_discord(gerar_have_carteira(pessoa))

                await message.channel.send(pessoa)
                await message.channel.send('\n\nHAVE\n')
                await message.channel.send(resposta)
            except Exception as error:
                await message.channel.send('QUACK! houve algum problema, tente novamente mais tarde.')
                print(error)

        if 'quack' in (str(message.content).lower()):
            await message.channel.send('QUACK Yeonji mencionada!!')
            await message.channel.send(file=discord.File('static/quack_gif.gif'))

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
