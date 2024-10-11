import os
from typing import Optional
import discord
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from datetime import date
from random import randint

from src.music import calendar
from src.cartola import cartola
from src.images import image_utils
from src.data.templates import templates
from src.data.idols import idolList

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
        gif_number = randint(1, 2)

        await message.channel.send('QUACK Yeonji mencionada!!')
        await message.channel.send(file=discord.File(f'static/quack_{gif_number}.gif'))

    if 'maluca' == (str(message.content).lower()):
        gif_number = randint(1, 5)

        await message.channel.send('MALUCA mencionada!!')
        await message.channel.send(file=discord.File(f'static/chaeyeon_{gif_number}.gif'))

    if 'medica' == (str(message.content).lower()) or 'médica' == (str(message.content).lower()):
        gif_number = randint(1, 5)

        await message.channel.send('MEDICA mencionada!!')
        await message.channel.send(file=discord.File(f'static/medica{gif_number}.gif'))

    if 'kaede' in (str(message.content).lower()) or 'kaebeça' in (str(message.content).lower()):
        await message.add_reaction('<:kaebeca:1234954376158773308>')

    if 'fleeky' in (str(message.content).lower()) or 'gang' in (str(message.content).lower()):
        await message.add_reaction('<:fleekabeca:1269741063946375188>')

    if 'r6' in (str(message.content).lower()):
        await message.add_reaction('<:peepoEvil:914947766386581504>')

    if 'fifinha' in (str(message.content).lower()):
        await message.add_reaction('⚽')

        if "?" in (str(message.content).lower()):
            await message.add_reaction('❓')

# --------------

    if '!fifa' == (str(message.content).lower()):
        user_ids = [701955314161025086, 321389614940028929, 1028533279802011688, 406686196581007361,
                    358470646549839874, 330886381075169284, 133033000114847744, 373560731196456980,
                    182935000046370816, 240929868957745155, 183630868114309120, 797942677844131911,
                    284441097545973762]

        mentions = " ".join([f"<@{user_id}>" for user_id in user_ids])

        await message.channel.send(f'{mentions}')
        await message.channel.send(file=discord.File('static/fifa.gif'))

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

@bot.tree.command(name='mercado', description='Veja quando o mercado irá fechar')
async def mercado(interaction: discord.Interaction):
    await interaction.response.defer()

    rodada_atual, fechamento, status_mercado, diferenca = await cartola.market_close_date()

    embed = discord.Embed(
        title=f'Mercado da {rodada_atual}ª rodada',
        color=0xccff66
    )

    embed.set_author(name=interaction.user.name,
                     icon_url=interaction.user.avatar)
    
    status_mercado_str = 'Aberto ✅' if status_mercado else 'Fechado ❌'

    embed.add_field(name='Status:', value=f'Mercado {status_mercado_str}', inline=False)
    
    if status_mercado:
        embed.add_field(name='Fechamento:', value=f'{fechamento}\n\nFalta: {diferenca}', inline=False)

    await interaction.followup.send(embed=embed)

# --------------


@bot.tree.command(name='tohrcarteira', description='Tohr dando carteirada.')
@app_commands.describe(usuario='Foto de perfil do usuário')
@app_commands.describe(imagem='Anexo da imagem')
async def tohrcarteira(interaction: discord.Interaction, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
    await interaction.response.defer()
    
    image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

    if not image:
        await interaction.followup.send("Forneça uma imagem válida!")
        return

    template = templates['tohr_carteira']

    await image_utils.reply_image(interaction=interaction, template=template, image=image)

@bot.tree.command(name='tohrreage', description='Tohr vai reagir')
@app_commands.describe(usuario='Foto de perfil do usuário')
@app_commands.describe(imagem='Anexo da imagem')
async def tohrreage(interaction: discord.Interaction, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
    await interaction.response.defer()

    image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

    if not image:
        await interaction.followup.send("Forneça uma imagem válida!")
        return

    template = templates['reacts'][randint(1, 4)]

    await image_utils.reply_image(interaction=interaction, template=template, image=image)



@bot.tree.command(name='idols', description='O que o idol está mostrando?')
@app_commands.describe(idol='Foto do idol')
@app_commands.describe(usuario='Foto de perfil do usuário')
@app_commands.describe(imagem='Anexo da imagem')
async def idols(interaction: discord.Interaction, idol: idolList, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
    await interaction.response.defer()  
    
    image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

    if not image:
        await interaction.followup.send("Forneça uma imagem válida!")
        return

    template = templates['idols'][idol]

    await image_utils.reply_image(interaction=interaction, template=template, image=image)
    
@bot.tree.command(name='cafe', description='Café para quem?')
@app_commands.describe(idol='Nome do idol')
async def cafe(interaction: discord.Interaction, idol: str):
    res = f"CADÊ MEU CAFÉ???? tá aqui sra. {idol}, do jeitinho que a senhora pediu, bota na mesa. Tá frio, vá buscar outro agora, sim senhora {idol}."

    await interaction.response.send_message(res)

bot.run(DISCORD_TOKEN)
