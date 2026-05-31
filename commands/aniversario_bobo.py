from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands

from src.aniversario_bobo.aniversario_banco import (
    deletar_aniversario,
    listar_aniversarios as buscar_aniversarios,
    salvar_aniversarios,
    setup_aniversario_database,
)

class AniversarioBobeira(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        setup_aniversario_database()

    @app_commands.command(description="Adicione ou edite um aniversário.")
    @app_commands.describe(data="Data no formato dd/mm")
    @app_commands.describe(id_usuario="ID de outro usuário (opcional)")
    async def adicionar_aniversario(self, interaction: discord.Interaction, data: str, id_usuario: str = None):
        await interaction.response.defer(ephemeral=True)

        try:
            datetime.strptime(data, "%d/%m")
        except ValueError:
                embed = discord.Embed(
                    title="Formato de data inválido! 🎂",
                    description="Por favor, use o formato **dd/mm** (ex: 25/12).",
                    color=discord.Color.red(),
                )
                return await interaction.followup.send(embed=embed, ephemeral=True)

        if id_usuario:
            user_id = id_usuario
        else:
            user_id = str(interaction.user.id)

        await salvar_aniversarios(user_id, data)
        username = self.bot.get_user(int(user_id)).display_name if self.bot.get_user(int(user_id)) else f"ID: {user_id}"
        embed = discord.Embed(
            title="Aniversário salvo! 🎂",
            description=f"Aniversário de {username} adicionado com sucesso: **{data}**",
            color=discord.Color.green(),
        )
        return await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(description="Remove seu aniversário da lista.")
    async def remover_aniversario(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        aniversarios = await buscar_aniversarios()
        aniversarios_ids = {aniversario_id for aniversario_id, _ in aniversarios}

        if user_id in aniversarios_ids:
            await deletar_aniversario(user_id)
            embed = discord.Embed(
                title="Aniversário removido! 🎂",
                description="Seu aniversário foi removido com sucesso.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Nenhum aniversário encontrado! 🎂",
                description="Você não tem um aniversário cadastrado.",
                color=discord.Color.orange(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Mostra a lista de aniversariantes.")
    async def listar_aniversarios(self, interaction: discord.Interaction):
        
        await interaction.response.defer()
        
        aniversarios = await buscar_aniversarios()

        if not aniversarios:
            embed = discord.Embed(
                title="Nenhum aniversário encontrado! 🎂",
                description="Nenhum aniversário cadastrado.",
                color=discord.Color.orange(),
            )
            await interaction.followup.send(embed=embed)
            return

        lista_ordenada = sorted(
            aniversarios,
            key=lambda item: datetime.strptime(item[1], "%d/%m")
        )
        
        message = ""

        for user_id, data in lista_ordenada:
            user = self.bot.get_user(int(user_id))
            username = user.display_name if user else (user.name if user else f"ID: {user_id}")
            message += f"- **{data}:** {username}\n"

        else:
            embed = discord.Embed(
                title="Lista de Aniversariantes 🎂",
                description=message,
                color=discord.Color.blue(),
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AniversarioBobeira(bot))