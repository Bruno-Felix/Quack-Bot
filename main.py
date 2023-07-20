import os
import discord
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

from utils.commands_strings import commands_idols, tripleS_idols, commands_wallets, season_cosmo_list, current_season_dict

from idol import search_idol_on_objekts_list, separate_idol_objekts_list_by_grids, separate_idol_objekts_list_by_idol
from wallets import get_all_wallets, get_one_wallet
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


# --------------

""" @app_commands.describe(
    id_cosmo = "Passe seu id no aplicativo do Cosmo",
    wallet_address = "Passe seu wallet address para entrar na lista. (App Cosmo -> My -> Copy the wallet address)",
)
@bot.tree.command(name = "inscrever", description = "Peça pra se inscrever na lista das carteiras do xet")
async def insert_wallet(interaction: discord.Interaction, id_cosmo: str, wallet_address: str):
    await interaction.response.send_message(f'{interaction.user.mention}{id_cosmo}{wallet_address}')
    # 1122561669210587157 """

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
    idol_objekts_list = search_idol_on_objekts_list(objekts_list, idol.name, season = season)

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

# --------

async def on_message(self, message):
    if 'quack' in (str(message.content).lower()):
        await message.channel.send('QUACK Yeonji mencionada!!')

bot.run(DISCORD_TOKEN)
