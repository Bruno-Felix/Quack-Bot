import os
import discord
from discord.ext import commands
from discord import app_commands
from src.utils.triples_colors import get_sort_triples_color

from src.quack_bet import quack_banco
from src.quack_bet.quack_banco import get_clubes_br_por_id

ESPORTES_CHANNEL_ID = os.getenv('ESPORTES_CHANNEL_ID')

class QuackBetApostas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        super().__init__()

    @app_commands.command(description='catalogar jogos')
    async def catalogar_jogos(self, interaction: discord.Interaction):
        await interaction.response.defer()

        novos_jogos = await quack_banco.catalogar_novos_jogos()

        embed = discord.Embed(
            title="Quack Bet • Jogos Catalogados <:brasileirao:1417954810803523795>",
            color=get_sort_triples_color()
        )

        embed.add_field(
            name=f"Jogos Catalogados",
            value=f"{novos_jogos} novos jogos",
            inline=False
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="registrar_resultado", description="Registra o resultado de um jogo e pontua os usuários")
    @app_commands.describe(
        partida_id="ID da partida",
        resultado="Resultado do jogo: 1, E ou 2"
    )
    async def registrar_resultado(self, interaction: discord.Interaction, partida_id: int, resultado: str):
        await interaction.response.defer()

        if resultado not in ("1", "E", "2"):
            await interaction.followup.send("❌ Resultado inválido. Use apenas: 1, E ou 2.")
            return

        try:
            res = await quack_banco.registrar_resultado(partida_id, resultado)
        except ValueError as e:
            await interaction.followup.send(f"❌ Erro: {e}")
            return
        
        time_casa = get_clubes_br_por_id(res['clube_casa'])
        time_visitante = get_clubes_br_por_id(res['clube_visitante'])

        embed = discord.Embed(
            title=f"{time_casa['emoji']} {time_casa['nome']} x {time_visitante['nome']} {time_visitante['emoji']}",
            description=f"Jogo com resultado registrado",
            color=0x1abc9c
        )
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=False)
        embed.add_field(
            name="Acertos",
            value=f"{res['acertadores']} usuários ganharam **{res['pontos_distribuidos']:.2f} pontos**",
            inline=False
        )

        await interaction.followup.send(embed=embed)



    async def postar_jogos(self):
        guild = self.bot.guilds[0]
        channel = guild.get_channel(int(ESPORTES_CHANNEL_ID))

        novos_jogos = await quack_banco.get_jogos_postagem()

        if novos_jogos:
            for jogo in novos_jogos:
                time_casa = get_clubes_br_por_id(jogo['clube_casa_id'])
                time_visitante = get_clubes_br_por_id(jogo['clube_visitante_id'])

                embed = discord.Embed(
                    title=f"{time_casa['emoji']} {time_casa['nome']} x {time_visitante['nome']} {time_visitante['emoji']}",
                    description=f"{jogo['partida_data']}",
                    color=get_sort_triples_color()
                )

                embed.set_footer(text=f"ID: {jogo['partida_id']}")

                mensagem = await channel.send(embed=embed)

                for emoji in ["1️⃣", "🇪", "2️⃣"]:
                    await mensagem.add_reaction(emoji)

                quack_banco.atualizar_message_id(jogo['partida_id'], mensagem.id)

    async def fechar_palpites(self):
        guild = self.bot.guilds[0]
        channel = guild.get_channel(int(ESPORTES_CHANNEL_ID))
        """ bot = self.bot
        thread = bot.get_channel(1466162540244631776) """

        jogos = await quack_banco.processar_palpites(self.bot)

        for jogo in jogos:
            partida_id = jogo["partida_id"]
            time_casa = get_clubes_br_por_id(jogo['clube_casa'])
            time_visitante = get_clubes_br_por_id(jogo['clube_visitante'])
            palpites = jogo["palpites"]

            embed = discord.Embed(
                title=f"{time_casa['emoji']} {time_casa['nome']} x {time_visitante['nome']} {time_visitante['emoji']}",
                description=f'Os palpites desse jogo foram encerrados!',
                color=0x1abc9c
            )

            embed.set_footer(text=f"ID: {partida_id}")

            embed.add_field(
                name="Palpites",
                value=f"1️⃣ → {palpites['1']}\n"
                    f"🇪 → {palpites['E']}\n"
                    f"2️⃣ → {palpites['2']}",
                inline=False
            )

            await channel.send(embed=embed)
            """ await thread.send(embed=embed) """

    @app_commands.command(name="listar_jogos", description="Lista jogos pelo status")
    @app_commands.describe(
        status="Status do jogo: 0=Cadastrado, 1=Postado, 2=Palpites encerrados, 3=Finalizado"
    )
    async def listar_jogos(self, interaction: discord.Interaction, status: int):
        await interaction.response.defer()

        if status not in (0, 1, 2, 3):
            await interaction.followup.send("❌ Status inválido. Use apenas: 0, 1, 2 ou 3.")
            return

        jogos = quack_banco.get_jogos_por_status(status)

        if not jogos:
            await interaction.followup.send("📭 Nenhum jogo encontrado com esse status.")
            return

        status_map = {
            0: "Cadastrados",
            1: "Postados",
            2: "Palpites encerrados",
            3: "Finalizados"
        }

        embed = discord.Embed(
            title=f"Quack Bet • Jogos {status_map[status]}",
            color=get_sort_triples_color()
        )

        for jogo in jogos[:20]:
            time_casa = get_clubes_br_por_id(jogo['clube_casa'])
            time_visitante = get_clubes_br_por_id(jogo['clube_visitante'])

            embed.add_field(
                name=f"{time_casa['emoji']} {time_casa['nome']} x {time_visitante['nome']} {time_visitante['emoji']}",
                value=f"📅 {jogo['partida_data']} | 🆔 {jogo['partida_id']} {jogo['message_id']}",
                inline=False
            )

        await interaction.followup.send(embed=embed)


    @app_commands.command(name="listar_usuarios", description="Lista todos os usuários cadastrados")
    async def listar_usuarios(self, interaction: discord.Interaction):
        await interaction.response.defer()

        usuarios = quack_banco.get_usuarios()

        if not usuarios:
            await interaction.followup.send("📭 Nenhum usuário encontrado.")
            return

        embed = discord.Embed(
            title="Quack Bet • Usuários",
            color=get_sort_triples_color()
        )

        for i, usuario in enumerate(usuarios[:20], start=1):
            embed.add_field(
                name=f"{i}. Usuário ID: {usuario['id']}",
                value=f"⭐ Pontos: {usuario['pontos']} | 🎯 Acertos: {usuario['acertos']}",
                inline=False
            )

        await interaction.followup.send(embed=embed)


    """ @app_commands.command(name="atualizar_usuario", description="Atualiza os pontos e acertos de um usuário")
    @app_commands.describe(
        user_id="ID do usuário",
        pontos="Novo total de pontos",
        acertos="Novo total de acertos"
    )
    async def atualizar_usuario(self, interaction: discord.Interaction, user_id: str, pontos: float, acertos: int):
        await interaction.response.defer(ephemeral=True)

        try:
            usuario = quack_banco.atualizar_usuario(user_id, pontos, acertos)
        except ValueError as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)
            return

        embed = discord.Embed(
            title="Quack Bet • Usuário Atualizado",
            color=get_sort_triples_color()
        )
        embed.add_field(name="Usuário", value=f"<@{usuario['id']}> ({usuario['id']})", inline=False)
        embed.add_field(name="Pontos", value=str(usuario['pontos']), inline=True)
        embed.add_field(name="Acertos", value=str(usuario['acertos']), inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True) """


    @app_commands.command(name="listar_palpites", description="Lista os palpites de um jogo")
    @app_commands.describe(jogo_id="ID do jogo no banco")
    async def listar_palpites(self, interaction: discord.Interaction, jogo_id: int):
        await interaction.response.defer(ephemeral=True)

        palpites = await quack_banco.listar_palpites_jogo(jogo_id)

        if not palpites:
            await interaction.followup.send("Nenhum palpite encontrado para este jogo.")
            return

        texto = f"📊 **Palpites do jogo {jogo_id}:**\n\n"
        for user_id, palpite in palpites:
            texto += f"• <@{user_id}> → `{palpite}`\n"

        await interaction.followup.send(texto)



async def setup(bot):
    await bot.add_cog(QuackBetApostas(bot))