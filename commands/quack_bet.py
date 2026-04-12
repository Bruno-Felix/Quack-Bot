import discord
from discord.ext import commands
from discord import app_commands
from static.quack_bet.times_br import get_clubes_br_por_id
from static.triples_colors import get_sort_triples_color

from src.quack_bet import quack_banco

class QuackBet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        quack_banco.setup_quack_bet_database()

        super().__init__()

    @app_commands.command(description='Mostra proximos jogos')
    async def proximos_jogos(self, interaction: discord.Integration):
        await interaction.response.defer()

        embed = discord.Embed(
            title="Quack Bet • Próximos Jogos <:brasileirao:1417954810803523795>",
            color=get_sort_triples_color()
        )

        lista_jogos = quack_banco.get_proximos_jogos()


        if not lista_jogos:
            embed.add_field(
                name=f"Sem jogos agendados",
                value=f"",
                inline=False
            )

        for jogo in lista_jogos:
            time_casa = get_clubes_br_por_id(jogo['clube_casa_id'])
            time_visitante = get_clubes_br_por_id(jogo['clube_visitante_id'])        

            embed.add_field(
                name=f"{time_casa['emoji']} {time_casa['nome']} x {time_visitante['nome']} {time_visitante['emoji']}",
                value=f"{jogo['partida_data']}",
                inline=False
            )

        await interaction.followup.send(embed=embed)


    @app_commands.command(description='Mostra o ranking do Quack Bet')
    @app_commands.describe(tipo="Escolha se o ranking será por pontos ou por acertos")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Acertos", value="acertos"),
        app_commands.Choice(name="Pontos", value="pontos")
    ])
    async def ranking_quack_bet(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):
        await interaction.response.defer()

        usuarios_db = quack_banco.get_ranking(tipo.value)

        if not usuarios_db:
            await interaction.followup.send("🦆 Ainda não há patos no lago.")
            return

        medalhas = ["👑", "🥈", "🥉", "", ""]
        top_ranking_numero = 3

        top_ranking = ""
        restante_top10 = ""
        restante = ""

        for idx, (user_id, valor) in enumerate(usuarios_db, start=1):
            user = await self.bot.fetch_user(int(user_id))
            nome = user.display_name

            medalha = medalhas[idx - 1] if idx <= top_ranking_numero else ""

            rotulo = "Pontos" if tipo.value == "pontos" else "Acertos"

            linha = (
                f"{idx:>2}º {nome:<20}"
                f"{int(valor) if tipo.value == 'acertos' else float(valor):<6.2f} {rotulo} {medalha}\n"
            )

            if idx <= top_ranking_numero:
                top_ranking += linha
            elif idx <= 10:
                restante_top10 += linha
            else:
                restante += linha

        descricao = (
            "```diff\n"
            f"{top_ranking}"
            "```"
            "```diff\n"
            f"{restante_top10}"
            "```"
            "```diff\n"
            f"{restante}"
            "```"
        )

        titulo = "Quack Bet • Ranking por Pontos 🦆" if tipo.value == "pontos" else "Quack Bet • Ranking por Acertos 🦆"

        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=get_sort_triples_color()
        )

        embed.set_footer(text=titulo)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(QuackBet(bot))