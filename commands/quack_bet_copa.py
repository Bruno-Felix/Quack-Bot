import os
import discord
from discord.ext import commands
from discord import app_commands
from src.utils.triples_colors import get_sort_triples_color

from src.quack_bet_copa import quack_copa_banco
from src.quack_bet_copa.palpite_views import PalpiteView, construir_embed_palpite

ESPORTES_CHANNEL_ID = os.getenv('ESPORTES_CHANNEL_ID')


class QuackBetCopa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        quack_copa_banco.setup_quack_bet_copa_database()
        quack_copa_banco.popular_selecoes_copa()
        quack_copa_banco.popular_jogos_copa()

        super().__init__()

    @app_commands.command(
        name="postar_rodada_copa",
        description="Começar Copa")
    @app_commands.describe(
        rodada="Coeçar Rodada (1, 2 ou 3)")
    async def postar_rodada_copa(self, interaction: discord.Interaction, rodada: int):
        if rodada is not None and rodada not in [1, 2, 3]:
            await interaction.response.send_message(
                "A rodada deve ser 1, 2 ou 3.",
                ephemeral=True
            )
            return
        
        novos_jogos = await quack_copa_banco.postar_rodada_copa(rodada)

        if novos_jogos:
            for jogo in novos_jogos:
                embed = discord.Embed(
                    title=(
                        f"{jogo['selecao_mandante_bandeira']} "
                        f"{jogo['selecao_mandante_nome']} 🆚 "
                        f"{jogo['selecao_visitante_nome']} "
                        f"{jogo['selecao_visitante_bandeira']}"
                    ),
                    description=(
                        f"Grupo {jogo['grupo_id']}\n"
                        f"📅 {jogo['partida_data']} às {jogo['partida_hora']}"
                    ),
                    color=get_sort_triples_color()
                )

                embed.set_footer(text=f"Rodada: {jogo['rodada_id']} | ID: {jogo['partida_id']}")

                mensagem = await interaction.channel.send(
                    embed=embed
                )

                for emoji in ["1️⃣", "🇪", "2️⃣"]:
                    await mensagem.add_reaction(emoji)

                quack_copa_banco.atualizar_message_id(jogo['partida_id'], mensagem.id)
        
    async def fechar_palpites_copa(self):
        guild = self.bot.guilds[0]
        channel = guild.get_channel(int(ESPORTES_CHANNEL_ID))
        jogos = await quack_copa_banco.processar_palpites_copa(self.bot)

        for jogo in jogos:
            embed = discord.Embed(
                title=(
                    f"{jogo['selecao_mandante_bandeira']} "
                    f"{jogo['selecao_mandante_nome']} 🆚 "
                    f"{jogo['selecao_visitante_nome']} "
                    f"{jogo['selecao_visitante_bandeira']}"
                ),
                description=(
                    f"Grupo {jogo['grupo_id']}\n"
                    f"📅 {jogo['partida_data']} às {jogo['partida_hora']}"
                ),
                color=get_sort_triples_color()
            )

            embed.set_footer(text=f"Rodada: {jogo['rodada_id']} | ID: {jogo['partida_id']}")

            palpites = jogo["palpites"]

            embed.add_field(
                name="Palpites",
                value=f"1️⃣ → {palpites['1']}\n"
                    f"🇪 → {palpites['E']}\n"
                    f"2️⃣ → {palpites['2']}",
                inline=False
            )

            await channel.send(embed=embed)
        

    @app_commands.command(name="palpite_copa", description="Abrir painel de palpite da Copa")
    async def palpite(self, interaction: discord.Interaction):
        quack_copa_banco.get_aposta_copa(str(interaction.user.id))

        embed = construir_embed_palpite(str(interaction.user.id))
        view = PalpiteView(str(interaction.user.id))

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True,
        )


    @app_commands.command(
        name="meus_palpites",
        description="Visualizar seus palpites da Copa")
    async def meus_palpites(self, interaction: discord.Interaction):
        aposta = quack_copa_banco.get_aposta_copa(str(interaction.user.id))

        embed = construir_embed_palpite(str(interaction.user.id))

        if aposta["finalizada"]:
            embed.title = "🏆 Meus Palpites da Copa"
            embed.description = (
                "Seu palpite já foi finalizado e não pode mais ser alterado."
            )
        else:
            embed.title = "🏆 Meus Palpites da Copa"

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(
        name="jogos_copa",
        description="Listar jogos da rodada")
    @app_commands.describe(
        rodada="Rodada da fase de grupos (1, 2 ou 3)",
        grupo="Grupo da Copa (A até L)")
    async def jogos_copa(self, interaction: discord.Interaction, rodada: int | None = None, grupo: str | None = None):
        if rodada is None and grupo is None:
            await interaction.response.send_message(
                "Informe pelo menos uma rodada ou grupo.\n\n"
                "Exemplos:\n"
                "`/jogos_copa rodada:1`\n"
                "`/jogos_copa grupo:A`\n"
                "`/jogos_copa rodada:2 grupo:F`",
                ephemeral=True
            )
            return

        if rodada is not None and rodada not in [1, 2, 3]:
            await interaction.response.send_message(
                "A rodada deve ser 1, 2 ou 3.",
                ephemeral=True
            )
            return

        
        if grupo:
            grupo = grupo.upper()

            if grupo not in list("ABCDEFGHIJKL"):
                await interaction.response.send_message(
                    "Grupo inválido. Utilize A até L.",
                    ephemeral=True
                )
                return
        
        jogos = quack_copa_banco.get_jogos(
                    rodada=rodada,
                    grupo=grupo
                )
        
        titulo = " Jogos da Copa"
        if rodada and grupo:
            titulo = f"Rodada {rodada} • Grupo {grupo}"
        elif rodada:
            titulo = f"Rodada {rodada}"
        elif grupo:
            titulo = f"Grupo {grupo}"
        embed = discord.Embed(
            title=f"<:copa:1512217994414260235> {titulo}",
            color=discord.Color.blue()
        )

        for (
            jogo_id,
            grupo,
            data,
            hora,
            casa_nome,
            casa_bandeira,
            visitante_nome,
            visitante_bandeira
        ) in jogos:

            embed.add_field(
                name=f"{casa_bandeira} {casa_nome} 🆚 {visitante_nome} {visitante_bandeira}",
                value=(f"Grupo {grupo} | 📅 {data} - {hora}\n"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed
        )


    @app_commands.command(
        name="copa_meus_palpites",
        description="Mostra seus palpites da rodada"
    )
    @app_commands.describe(
        rodada="Rodada da fase de grupos (1, 2 ou 3)"
    )
    async def copa_meus_palpites(
        self,
        interaction: discord.Interaction,
        rodada: int
    ):
        if rodada not in [1, 2, 3]:
            await interaction.response.send_message(
                "A rodada deve ser 1, 2 ou 3.",
                ephemeral=True
            )
            return

        palpites = quack_copa_banco.get_meus_palpites(
            interaction.user.id,
            rodada
        )

        if not palpites:
            await interaction.response.send_message(
                f"Você ainda não realizou palpites para a rodada {rodada}.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🏆 Meus Palpites - Rodada {rodada}",
            color=discord.Color.gold()
        )

        emoji_palpite = {
            "1": "1️⃣",
            "E": "🇪",
            "2": "2️⃣"
        }

        for (
            partida_id,
            grupo_id,
            partida_data,
            partida_hora,
            palpite,
            casa_nome,
            casa_bandeira,
            visitante_nome,
            visitante_bandeira
        ) in palpites:

            embed.add_field(
                name=(
                    f"{casa_bandeira} {casa_nome} "
                    f"🆚 "
                    f"{visitante_nome} {visitante_bandeira}"
                ),
                value=(
                    f"Grupo {grupo_id}\n"
                    f"📅 {partida_data} às {partida_hora}\n"
                    f"🎯 Palpite: {emoji_palpite.get(palpite, palpite)}"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
        )


async def setup(bot):
    await bot.add_cog(QuackBetCopa(bot))