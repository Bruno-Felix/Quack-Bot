import discord
from discord.ext import commands
from discord import app_commands
from datetime import date, datetime
from zoneinfo import ZoneInfo

from static.triples_colors import get_sort_triples_color
from src.music import calendar

brasilia_tz = ZoneInfo("America/Sao_Paulo")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @app_commands.command(description='Veja os lançamentos de kpop do dia')
    async def hoje(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = discord.Embed(
            title='Lançamentos!!',
            description='Todos os lançamentos de hoje\n',
            color=get_sort_triples_color()
        )

        search_date = str(datetime.now(brasilia_tz).date())
        # search_date = date(2024, 12, 18).strftime("%Y-%m-%d")

        results = await calendar.get_daily_kpop_calendar(search_date)

        embed.set_author(name=interaction.user.name,
                        icon_url=interaction.user.avatar)

        for result in results:
            embed.add_field(name="\u200b", value=result, inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(description='Veja os lançamentos de kpop da semana')
    async def semana(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = discord.Embed(
            title='Lançamentos!!',
            description='Todos os lançamentos dessa proxima semana\n',
            color=get_sort_triples_color()
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


async def setup(bot):
    await bot.add_cog(Music(bot))