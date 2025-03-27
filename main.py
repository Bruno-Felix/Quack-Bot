import os
import discord
import asyncio
import schedule
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands

from src.commands.music import Music
from src.schedule import schedule_today_musics, schedule_change_idol_guess_for_today

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


@bot.event
async def on_ready():
    try:
        await load_commands()

        synced = await bot.tree.sync()

        print(f'\nQuack Bot pronta!! Conectado como {bot.user}')
        print(f'{len(synced)} comandos sincronizados')

        bot.loop.create_task(schedule_today_musics(bot))
        bot.loop.create_task(schedule_change_idol_guess_for_today(bot))
    except Exception as error:
        print(error)


bot.run(DISCORD_TOKEN)