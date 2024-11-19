import discord
from discord.ext import commands
from discord import app_commands

from src.cartola import cartola

class Cartola(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @app_commands.command(description='Veja quando o mercado do cartola irá fechar')
    async def cartola(self, interaction: discord.Interaction):
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


async def setup(bot):
    await bot.add_cog(Cartola(bot))