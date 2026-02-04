import os
import discord
from discord.ext import commands
from discord import app_commands
from static.quack_bet.times_br import get_clubes_br_por_id
from static.triples_colors import get_sort_triples_color

from src.quack_bet import quack_banco

ESPORTES_CHANNEL_ID = os.getenv('ESPORTES_CHANNEL_ID')

class QuackBetApostas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        super().__init__()

    @app_commands.command(description='catalogar jogos')
    async def catalogar_jogos(self, interaction: discord.Integration):
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
        jogo_id="ID do jogo",
        resultado="Resultado do jogo: 1, E ou 2"
    )
    async def registrar_resultado_cmd(self, interaction: discord.Interaction, jogo_id: int, resultado: str):
        await interaction.response.defer()

        if resultado not in ("1", "E", "2"):
            await interaction.followup.send("❌ Resultado inválido. Use apenas: 1, E ou 2.")
            return

        try:
            res = await quack_banco.registrar_resultado(jogo_id, resultado)
        except ValueError as e:
            await interaction.followup.send(f"❌ Erro: {e}")
            return

        embed = discord.Embed(
            title="Quack Bet • Jogo Finalizado 🏁",
            description=f"O jogo **{res['clube_casa']} x {res['clube_visitante']}** foi finalizado!",
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

            embed.add_field(
                name="Palpites",
                value=f"1️⃣ → {palpites['1']}\n"
                    f"🇪 → {palpites['E']}\n"
                    f"2️⃣ → {palpites['2']}",
                inline=False
            )

            await channel.send(embed=embed)
            """ await thread.send(embed=embed) """


async def setup(bot):
    await bot.add_cog(QuackBetApostas(bot))