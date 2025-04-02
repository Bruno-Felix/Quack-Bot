from datetime import date, datetime
from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands

from src.idol_aniversario.idols_birthday import aniversario_scraping


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
            data_title = "de hoje!"

            print(res)

            embed = discord.Embed(
                title=f'Aniversariantes {data_title}',
                color=0xccff66
            )
            embed.add_field(name="Parabéns!", value=res[6:])
            await interaction.followup.send(embed=embed)

        elif data == "Mês":
            res = await aniversario_scraping("", date.today().month)
            data_title = "do mês!"

            if len(res) > 1024:
                pages = self.split_text_by_newline(res, 1024)

                await self.send_paginated_embeds(interaction, pages, data_title)
            else:
                embed = discord.Embed(
                    title=f'Aniversariantes {data_title}',
                    color=0xccff66
                )
                embed.add_field(name="Parabéns!", value=res)
                await interaction.followup.send(embed=embed)

        elif dia_especifico:
            try:
                dia, mes = dia_especifico.split("/")
                datetime.strptime(dia, "%d")
                datetime.strptime(mes, "%m")
            except ValueError:
                await interaction.followup.send("Data inválida. Digite no formato dd/mm")
                return

            data_title = f"de {dia}/{mes}!"
            res = await aniversario_scraping(dia, mes)

            embed = discord.Embed(
                title=f'Aniversariantes {data_title}',
                color=0xccff66
            )
            embed.add_field(name="Parabéns!", value=res[6:])
            await interaction.followup.send(embed=embed)

    def split_text_by_newline(self, text: str, max_length: int) -> list[str]:

        pages = []
        while len(text) > max_length:
            split_index = text.rfind("\n", 0, max_length)
            if split_index == -1:
                split_index = max_length

            pages.append(text[:split_index].strip())
            text = text[split_index:].strip()

        if text:
            pages.append(text)
        return pages

    async def send_paginated_embeds(self, interaction: discord.Interaction, pages: list[str], title: str):

        current_page = 0
        total_pages = len(pages)

        def create_embed(page: int):
            embed = discord.Embed(
                title=f'Aniversariantes {title} (Página {page + 1}/{total_pages})',
                color=0xccff66
            )
            embed.add_field(name="Parabéns!", value=pages[page])
            return embed

        message = await interaction.followup.send(embed=create_embed(current_page))

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("❌")

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda r, u: u == interaction.user and r.message.id == message.id and str(r.emoji) in ["⬅️", "➡️", "❌"]
                )

                if str(reaction.emoji) == "➡️":
                    current_page = (current_page + 1) % total_pages
                elif str(reaction.emoji) == "⬅️":
                    current_page = (current_page - 1) % total_pages
                elif str(reaction.emoji) == "❌":
                    await message.delete()
                    return

                await message.edit(embed=create_embed(current_page))
                await message.remove_reaction(reaction.emoji, user)

            except TimeoutError:
                await message.clear_reactions()
                break


async def setup(bot):
    await bot.add_cog(AniversarioIdol(bot))