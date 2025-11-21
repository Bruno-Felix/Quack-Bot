from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands

# Carrega aniversários do arquivo CSV
aniversarios = {}
with open('static/aniversarios.csv', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            id, data = line.split(',')
            aniversarios[id] = data

class AniversarioXet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Adicione ou edite seu aniversário.")
    @app_commands.describe(data="Data no formato dd/mm")
    async def adicionar_aniversario(self, interaction: discord.Interaction, data: str):
        await interaction.response.defer(ephemeral=True)

        try:
            datetime.strptime(data, "%d/%m")
        except ValueError:
            await interaction.followup.send("Formato inválido. Use dd/mm.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        aniversarios[user_id] = data

        # Salva todo o dicionário no CSV
        with open('static/aniversarios.csv', 'w', encoding='utf-8') as f:
            for id, data in aniversarios.items():
                f.write(f"{id},{data}\n")

        await interaction.followup.send(f"Aniversário adicionado: {data}", ephemeral=True)

    @app_commands.command(description="Remove seu aniversário da lista.")
    async def remover_aniversario(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id in aniversarios:
            del aniversarios[user_id]
            with open('static/aniversarios.csv', 'w', encoding='utf-8') as f:
                for id, data in aniversarios.items():
                    f.write(f"{id},{data}\n")
            await interaction.response.send_message("Aniversário removido.", ephemeral=True)
        else:
            await interaction.response.send_message("Nenhum aniversário cadastrado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AniversarioXet(bot))