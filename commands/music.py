import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import date, datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from static.triples_colors import get_sort_triples_color
from src.music import calendar

brasilia_tz = ZoneInfo("America/Sao_Paulo")

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

QUACK_BOT_CHANNEL_ID = os.getenv('QUACK_BOT_CHANNEL_ID')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    async def hoje_diario(self):
        guild = self.bot.guilds[0]
        channel = guild.get_channel(int(QUACK_BOT_CHANNEL_ID))

        embed = discord.Embed(
            title='Lançamentos do dia!!',
            description='Fique de olho em todos os lançamentos de hoje\n',
            color=get_sort_triples_color()
        )

        search_date = str(datetime.now(brasilia_tz).date())

        results = await calendar.get_daily_kpop_calendar(search_date)

        for result in results:
            embed.add_field(name="\u200b", value=result, inline=False)

        if channel:
            await channel.send(embed=embed)

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

        if results:
            for result in results:
                embed.add_field(name="\u200b", value=result, inline=False)
        else:
            embed.add_field(name="\u200b", value='Sem lançamentos hoje!!', inline=False)

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