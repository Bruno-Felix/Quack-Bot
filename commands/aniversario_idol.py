from datetime import date, datetime
from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands

from src.paginator import split_text_by_newline, send_paginated_embeds
from src.aniversario.idols_birthday import aniversario_scraping

class AniversarioIdol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(description='Veja os aniversariantes do dia ou do mês')
    @app_commands.describe(data="Hoje ou Mês")
    @app_commands.describe(dia_especifico="Dia específico (dd/mm)")
    async def aniversario_idol(self, interaction: discord.Interaction, data: Optional[Literal["Hoje", "Mês"]] = None, dia_especifico: Optional[str] = None):
        await interaction.response.defer()

        if data == "Hoje":
            dia = date.today().day
            mes = date.today().month
            res = await aniversario_scraping(dia, mes)

            embed = discord.Embed(
                title='Aniversariantes de hoje!',
                color=0xccff66
            )
            embed.add_field(name="Parabéns!", value=res[6:]) 
            await interaction.followup.send(embed=embed)

        elif data == "Mês":
            res = await aniversario_scraping("", date.today().month)

            if len(res) > 1024:
                pages = split_text_by_newline(res, 1024)
                
                await send_paginated_embeds(interaction, pages, "Aniversariantes do mês!")
            else:
                embed = discord.Embed(
                    title='Aniversariantes do mês!',
                    color=0xccff66
                )
                embed.add_field(name="Parabéns!", value=res)
                await interaction.followup.send(embed=embed)

        elif dia_especifico:
            try:
                datetime.strptime(dia_especifico, "%d/%m")
                dia, mes = dia_especifico.split("/")
            except ValueError:
                await interaction.followup.send("Data inválida ou formato incorreto. Use dd/mm (Ex: 25/12).")
                return

            res = await aniversario_scraping(int(dia), int(mes))

            embed = discord.Embed(
                title=f'Aniversariantes de {dia}/{mes}!',
                color=0xccff66
            )
            embed.add_field(name="Parabéns!", value=res[6:])
            await interaction.followup.send(embed=embed)
        
        else:
            await interaction.followup.send("Por favor, selecione 'Hoje', 'Mês' ou digite uma data específica.")

async def setup(bot):
    await bot.add_cog(AniversarioIdol(bot))