import discord, os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from static.triples_colors import get_sort_triples_color
from src.cartola import cartola
from src.mentions import get_users_by_reaction

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

ESPORTES_CHANNEL_ID = os.getenv('ESPORTES_CHANNEL_ID')
CARTOLA_REACTIONS_MESSAGE_ID = os.getenv('CARTOLA_REACTIONS_MESSAGE_ID')

class Cartola(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @app_commands.command(description='Veja quando o mercado do cartola irá fechar')
    async def cartola(self, interaction: discord.Interaction):
        await interaction.response.defer()

        rodada_atual, fechamento, status_mercado, diferenca, _ = await cartola.market_close_date()

        embed = discord.Embed(
            title=f'Mercado da {rodada_atual}ª rodada',
            color=get_sort_triples_color()
        )

        embed.set_author(name=interaction.user.name,
                        icon_url=interaction.user.avatar)
        
        status_mercado_str = 'Aberto ✅' if status_mercado else 'Fechado ❌'

        embed.add_field(name='Status:', value=f'Mercado {status_mercado_str}', inline=False)
        
        if status_mercado:
            embed.add_field(name='Fechamento:', value=f'{fechamento}\n\nFalta: {diferenca}', inline=False)

        await interaction.followup.send(embed=embed)

    async def call_rodada_cartola(self):
        guild = self.bot.guilds[0]
        channel = guild.get_channel(int(ESPORTES_CHANNEL_ID))

        _, fechamento, status_mercado, _, diferenca_date_time = await cartola.market_close_date()
        
        if status_mercado:
            diferenca_horas = (diferenca_date_time.total_seconds() // 3600) + 3
            print('Cartola:', fechamento, diferenca_horas)
            
            if diferenca_horas == 2 or diferenca_horas == 24:
                mentions = await get_users_by_reaction(self, ESPORTES_CHANNEL_ID, CARTOLA_REACTIONS_MESSAGE_ID, "🎩")

                message = f'Não deixe de escalar o Cartola!!\nO mercado fechará {fechamento}.\n{mentions}'
                await channel.send(message)


# --------------


async def setup(bot):
    await bot.add_cog(Cartola(bot))