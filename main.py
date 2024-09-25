import os
import discord
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from datetime import date
from random import randint

from src.music import calendar

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()

        print(f'Quack Bot pronta!! Conectado como {bot.user}')
        print(f'{len(synced)} comandos sincronizados')
    except Exception as error:
        print(error)


# --------------

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if 'quack' == (str(message.content).lower()):
        await message.channel.send('QUACK Yeonji mencionada!!')
        await message.channel.send(file=discord.File(f'static/quack_{1}.gif'))

    if 'maluca' in (str(message.content).lower()):
        await message.add_reaction('<:tohrn1S4:1104808399343996938>')
        if 'maluca' == (str(message.content).lower()):
            gif_number = randint(1, 5)

            await message.channel.send('MALUCA mencionada!!')
            await message.channel.send(file=discord.File(f'static/chaeyeon_{gif_number}.gif'))

    if 'medica' in (str(message.content).lower()):
        await message.add_reaction('<:tohrn1OK:1158268768779239544>')
        if 'medica' == (str(message.content).lower()):
            gif_number = randint(1, 5)

            await message.channel.send('MEDICA mencionada!!')
            await message.channel.send(file=discord.File(f'static/medica{gif_number}.gif'))

    if 'kaede' in (str(message.content).lower()) or 'kaebeça' in (str(message.content).lower()):
        await message.add_reaction('<:kaebeca:1234954376158773308>')

    if '!fifa' == (str(message.content).lower()):
        user_ids = [701955314161025086, 321389614940028929, 1028533279802011688, 406686196581007361,
                    358470646549839874, 330886381075169284, 133033000114847744, 373560731196456980,
                    182935000046370816, 240929868957745155, 183630868114309120, 797942677844131911,
                    284441097545973762]

        mentions = " ".join([f"<@{user_id}>" for user_id in user_ids])

        await message.channel.send(f'{mentions}')
        await message.channel.send(file=discord.File('static/fifa1.gif'))

    if "!live" == (str(message.content).lower()):
        await message.channel.send(file=discord.File('static/tohrjob.gif'))


# --------------


@bot.tree.command(name='hoje', description='Veja os lançamentos de kpop do dia')
async def cosmo(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title='Lançamentos!!',
        description='Todos os lançamentos de hoje\n',
        color=0xccff66
    )

    search_date = date.today().strftime("%Y-%m-%d")
    # search_date = date(2024, 9, 19).strftime("%Y-%m-%d")

    results = await calendar.get_daily_kpop_calendar(search_date)

    embed.set_author(name=interaction.user.name,
                     icon_url=interaction.user.avatar)
    embed.add_field(name='Hoje temos:', value=results)

    await interaction.followup.send(embed=embed)

# --------------


@bot.tree.command(name='semana', description='Veja os lançamentos de kpop da semana')
async def cosmo(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title='Lançamentos!!',
        description='Todos os lançamentos dessa proxima semana\n',
        color=0xccff66
    )

    search_start_date = date.today()

    results = await calendar.get_weekly_kpop_calendar(search_start_date)

    embed.set_author(name=interaction.user.name,
                     icon_url=interaction.user.avatar)

    for dia, eventos in results.items():
        eventos_str = "\n".join(
            eventos) if eventos else "Sem lançamentos nessa data"

        embed.add_field(name=f"{dia}:", value=eventos_str, inline=False)

    await interaction.followup.send(embed=embed)

# --------------

bot.run(DISCORD_TOKEN)
