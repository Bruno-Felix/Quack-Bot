import os
import discord
from random import randint
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

from utils.commands_strings import commands_idols, tripleS_idols, commands_wallets, season_cosmo_list, current_season_dict
from utils.objekts import special_price, double_price, first_price

from idol import search_idol_on_objekts_list, separate_idol_objekts_list_by_grids, separate_idol_objekts_list_by_idol
from wallets import get_all_wallets, get_one_wallet, read_wallet_price
from bot_response import response_bot_search_idol_objekts, response_bot_wallet_by_idol

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        
        print(f'Estou pronto! Estou conectado como {bot.user}')
        print(f'Synced {len(synced)} commands')
    except Exception as error:
        print(error)


# --------


@bot.event
async def on_message(message):
    if message.author == bot.user:
            return

    if 'quack' in (str(message.content).lower()):
        await message.channel.send('QUACK Yeonji mencionada!!')
        await message.channel.send(file=discord.File(f'static/quack_{1}.gif'))

    if 'maluca' in (str(message.content).lower()):
        gif_number = randint(1,5)

        await message.channel.send('MALUCA mencionada!!')
        await message.channel.send(file=discord.File(f'static/chaeyeon_{1}.gif'))

    if 'medica' in (str(message.content).lower()):
        gif_number = randint(1,5)

        await message.channel.send('MEDICA mencionada!!')
        await message.channel.send(file=discord.File(f'static/medica_{1}.gif'))

    #if 'show do Twice' in (str(message.content).lower()):
    #    await message.channel.send('06/02 ELAS VIRÃO!!')
    #    await message.channel.send(file=discord.File(f'static/twice.gif'))

# --------------


idol_options = []
for index, a in enumerate(commands_idols):
    idol_options.append(app_commands.Choice(name = f"{a}", value = f"{index + 1}"))

season_options = []
for index, a in enumerate(season_cosmo_list):
    season_options.append(app_commands.Choice(name = f"{a}", value = f"{index + 1}"))

@app_commands.describe(
    idol = "Selecione o idol que deseja procurar",
    temporada = "Selecione a temporada do objekt que deseja procurar"
)
@app_commands.choices(idol = idol_options, temporada = season_options)
@bot.tree.command(name = 'cosmo', description = 'Busque quem do xet tem o objekt da integrante que você deseja')
async def cosmo(interaction: discord.Interaction, idol: app_commands.Choice[str], temporada: app_commands.Choice[str] = None):
    await interaction.response.defer()

    # --- code ---
    season = current_season_dict['tripleS'] if idol.name in tripleS_idols else current_season_dict['artms']
    season = temporada.name if temporada else season

    objekts_list = get_all_wallets()
    print('search_idol_on_objekts_list')
    idol_objekts_list = search_idol_on_objekts_list(objekts_list, idol.name, season = season)

    print('separate_idol_objekts_list_by_grids')
    grid_1, grid_2, grid_3 = separate_idol_objekts_list_by_grids(idol_objekts_list)
    grid_1, grid_2, grid_3 = response_bot_search_idol_objekts(grid_1, grid_2, grid_3)
    # --- code ---

    embed = discord.Embed(
        title = f'{idol.name} ({season})',
        color = 0xddddd
    )

    file = discord.File("static/cosmo.png", filename = "image.png")
    embed.set_thumbnail(url = "attachment://image.png")
    
    embed.set_author(name = interaction.user.name, icon_url = interaction.user.avatar)
    embed.add_field(name = '101 a 108', value = grid_1)
    embed.add_field(name = '109 a 116', value = grid_2)
    embed.add_field(name = '117 a 120', value = grid_3, inline = False)
    
    await interaction.followup.send(embed = embed, file = file)


# --------------


wallet_options = []
for index, wallet in enumerate(commands_wallets):
    wallet_options.append(app_commands.Choice(name = f"{wallet}", value = f"{index + 1}"))

@app_commands.describe(
    usuario = "Selecione o usuario que deseja ver a carteira",
)
@app_commands.choices(usuario = wallet_options)
@bot.tree.command(name = 'carteira', description = 'Veja os FCOs da carteira de uma pessoa')
async def cosmo(interaction: discord.Interaction, usuario: app_commands.Choice[str]):
    await interaction.response.defer()

    # --- code ---
    objekts_list = get_one_wallet(usuario.name)
    objekts_list_by_idol = separate_idol_objekts_list_by_idol(objekts_list)
    response_bot = response_bot_wallet_by_idol(objekts_list_by_idol)
    # --- code ---

    embed = discord.Embed(
        title = usuario.name,
        color = 0x0099ff
    )

    file = discord.File("static/cosmo.png", filename = "image.png")
    embed.set_thumbnail(url = "attachment://image.png")

    embed.set_author(name = interaction.user.name, icon_url = interaction.user.avatar)
    embed.add_field(name = 'Have', value = response_bot)
    
    await interaction.followup.send(embed = embed, file = file)


# --------------


wallet_options = []
for index, wallet in enumerate(commands_wallets):
    wallet_options.append(app_commands.Choice(name = f"{wallet}", value = f"{index + 1}"))

@app_commands.describe(
    usuario = "Selecione o usuario que deseja ver o preço da carteira",
)
@app_commands.choices(usuario = wallet_options)
@bot.tree.command(name = 'preco', description = 'Veja o preço da carteira')
async def preco(interaction: discord.Interaction, usuario: app_commands.Choice[str]):
    await interaction.response.defer()

    # --- code ---
    price, special_objekt_count, double_objekt_count, first_objekt_count =  read_wallet_price(usuario.name)
    # --- code ---

    embed = discord.Embed(
        title = usuario.name,
        color = 0x0099ff
    )

    file = discord.File("static/cosmo.png", filename = "image.png")
    embed.set_thumbnail(url = "attachment://image.png")

    embed.set_author(name = interaction.user.name, icon_url = interaction.user.avatar)

    embed.add_field(name = f'Special ({special_price} reais)', value = special_objekt_count)
    embed.add_field(name = f'Double ({double_price} reais)', value = double_objekt_count)
    embed.add_field(name = f'First ({first_price} reais)', value = first_objekt_count)

    embed.add_field(name = 'Preço', value = f'{price} reais')

    await interaction.followup.send(embed = embed, file = file)


bot.run(DISCORD_TOKEN)
