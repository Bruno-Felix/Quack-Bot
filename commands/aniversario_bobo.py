from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
import os

from src.paginator import split_text_by_newline, send_paginated_embeds

class AniversarioXet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.arquivo_csv = 'static/aniversarios.csv'
        self.aniversarios = {} 
        self.carregar_aniversarios() 

    def carregar_aniversarios(self):
        self.aniversarios = {}
        
        if not os.path.exists(self.arquivo_csv):
            return

        try:
            with open(self.arquivo_csv, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            user_id, data = line.split(',')
                            self.aniversarios[user_id] = data
                        except ValueError:
                            continue 
        except Exception as e:
            print(f"Erro ao carregar aniversários: {e}")

    def salvar_aniversarios(self):
        try:
            with open(self.arquivo_csv, 'w', encoding='utf-8') as f:
                for user_id, data in self.aniversarios.items():
                    f.write(f"{user_id},{data}\n")
        except Exception as e:
            print(f"Erro ao salvar aniversários: {e}")

    @app_commands.command(description="Adicione ou edite seu aniversário.")
    @app_commands.describe(data="Data no formato dd/mm")
    async def adicionar_aniversario(self, interaction: discord.Interaction, data: str):
        await interaction.response.defer(ephemeral=True)

        try:
            datetime.strptime(data, "%d/%m")
        except ValueError:
            await interaction.followup.send("Formato inválido. Use dd/mm (Ex: 25/12).", ephemeral=True)
            return

        self.carregar_aniversarios()

        user_id = str(interaction.user.id)
        self.aniversarios[user_id] = data
        
        self.salvar_aniversarios()

        await interaction.followup.send(f"Aniversário adicionado: {data}", ephemeral=True)

    @app_commands.command(description="Remove seu aniversário da lista.")
    async def remover_aniversario(self, interaction: discord.Interaction):
        self.carregar_aniversarios()
        
        user_id = str(interaction.user.id)
        
        if user_id in self.aniversarios:
            del self.aniversarios[user_id]
            self.salvar_aniversarios()
            await interaction.response.send_message("Aniversário removido.", ephemeral=True)
        else:
            await interaction.response.send_message("Nenhum aniversário cadastrado para você.", ephemeral=True)

    @app_commands.command(description="Mostra a lista de aniversariantes.")
    async def listar_aniversarios(self, interaction: discord.Interaction):
        
        await interaction.response.defer()
        
        self.carregar_aniversarios()

        if not self.aniversarios:
            await interaction.followup.send("Nenhum aniversário cadastrado.")
            return

        lista_ordenada = sorted(
            self.aniversarios.items(),
            key=lambda item: datetime.strptime(item[1], "%d/%m")
        )

        message = "**Lista de Aniversariantes:**\n"
        
        for user_id, data in lista_ordenada:
            user = self.bot.get_user(int(user_id))
            username = user.display_name if user else (user.name if user else f"ID: {user_id}")
            message += f"- **{data}:** {username}\n"

        if len(message) > 1024:
            pages = split_text_by_newline(message, 1024)
            await send_paginated_embeds(interaction, pages, "Aniversariantes")
        else:
            await interaction.followup.send(message)

async def setup(bot):
    await bot.add_cog(AniversarioXet(bot))