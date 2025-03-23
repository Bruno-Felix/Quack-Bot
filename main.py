import os
import discord
import asyncio
import schedule
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands

from src.commands.music import Music

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def load_commands():
    for arquivo in os.listdir('src/commands'):
        if arquivo.endswith('.py'):
            print(f'commands.{arquivo[:-3]}')

            await bot.load_extension(f'src.commands.{arquivo[:-3]}')


async def schedule_loop():
    print('schedule sincronizado')
    music_cog = bot.get_cog("Music")

    schedule.every().day.at("11:00").do(lambda: asyncio.create_task(music_cog.hoje_diario()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(60)


@bot.event
async def on_ready():
    try:
        await load_commands()

        synced = await bot.tree.sync()

        print(f'\nQuack Bot pronta!! Conectado como {bot.user}')
        print(f'{len(synced)} comandos sincronizados')

        await bot.loop.create_task(schedule_loop())
    except Exception as error:
        print(error)


bot.run(DISCORD_TOKEN)