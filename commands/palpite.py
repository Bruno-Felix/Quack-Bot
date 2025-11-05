import discord
from discord.ext import commands
from discord import app_commands
from src.palpites import palpites_banco
from src.palpites import endpoints_palpites
from src.palpites.times import get_team_by_id
from static.triples_colors import get_sort_triples_color

class Palpite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        palpites_banco.setup_rodadas_database()

    @app_commands.command(description='Mostra os jogos da rodada do Brasileirão')
    async def jogos_rodada(self, interaction: discord.Interaction):
        await interaction.response.defer()

        jogos = await endpoints_palpites.request_clubes_e_prox_rodada()

        embed = discord.Embed(
            title='Jogos da rodada',
            color=get_sort_triples_color()
        )

        for partida in jogos:
            casa = get_team_by_id(partida['clube_casa_id'])
            visitante = get_team_by_id(partida['clube_visitante_id'])
            embed.add_field(
                name=f"{casa['nome_fantasia']} x {visitante['nome_fantasia']}",
                value=f"🕒 {partida['partida_data']}",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(description="🟢 Cria uma nova rodada de palpites")
    async def criar_rodada(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # ✅ avisa ao Discord que estamos processando

        rodada_aberta = palpites_banco.get_rodada_aberta()
        if rodada_aberta:
            await interaction.followup.send("⚠️ Já existe uma rodada aberta!", ephemeral=True)
            return
        
        numero_rodada = 1 if not rodada_aberta else rodada_aberta[1] + 1
        palpites_banco.criar_rodada(numero_rodada)

        jogos = await endpoints_palpites.request_clubes_e_prox_rodada()
        for partida in jogos:
            # Pega os nomes dos times
            casa = get_team_by_id(partida['clube_casa_id'])
            visitante = get_team_by_id(partida['clube_visitante_id'])

            # Insere o jogo no banco e pega o ID
            jogo_id = palpites_banco.inserir_jogo(
                numero_rodada,
                casa['nome_fantasia'],
                visitante['nome_fantasia'],
                partida['partida_data']
            )

            # Envia a mensagem no Discord
            msg = await interaction.channel.send(
                f"**{casa['nome_fantasia']} x {visitante['nome_fantasia']}**\n"
                f"🕒 {partida['partida_data']}\n\n"
                "Reaja com:\n"
                "1️⃣ Mandante vence\n"
                "🇪 Empate\n"
                "2️⃣ Visitante vence"
            )

            # Adiciona as reações
            for emoji in ["1️⃣", "🇪", "2️⃣"]:
                await msg.add_reaction(emoji)

            # Atualiza o jogo com o message_id
            palpites_banco.atualizar_message_id(jogo_id, msg.id)

        await interaction.followup.send("✅ Nova rodada criada e mensagens enviadas!", ephemeral=True)


    @app_commands.command(description="🔒 Fecha a rodada atual e salva os palpites")
    async def fechar_rodada(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        rodada_id = palpites_banco.fechar_rodada()
        if not rodada_id:
            await interaction.followup.send("⚠️ Não há rodada aberta.", ephemeral=True)
            return

        jogos = palpites_banco.get_jogos_da_rodada(rodada_id)
        if not jogos:
            await interaction.followup.send("❌ Nenhum jogo encontrado para essa rodada.", ephemeral=True)
            return

        channel = interaction.channel

        print('Salvar jogos', len(jogos))
        for jogo_id, message_id in jogos:
            print('jogo', jogo_id)
            if not message_id:
                print(f"❌ Jogo {jogo_id} não tem message_id definido, pulando...")
                continue

            try:
                message = await channel.fetch_message(int(message_id))
            except Exception as e:
                print(f"Erro ao buscar mensagem {message_id}: {e}")
                continue

            for reaction in message.reactions:
                if str(reaction.emoji) not in ["1️⃣", "🇪", "2️⃣"]:
                    continue

                async for user in reaction.users():
                    if user.bot:
                        continue

                    palpite = (
                        "1" if str(reaction.emoji) == "1️⃣"
                        else "E" if str(reaction.emoji) == "🇪"
                        else "2"
                    )

                    palpites_banco.salvar_palpite(str(user.id), jogo_id, palpite)

        await interaction.followup.send(f"🔒 Rodada {rodada_id} foi fechada! Todos os palpites foram salvos.", ephemeral=True)


    @app_commands.command(description="📊 Mostra seus palpites da última rodada")
    async def meus_palpites(self, interaction: discord.Interaction):
        rodada_aberta = palpites_banco.get_rodada_aberta()
        if rodada_aberta:
            await interaction.response.send_message("⚠️ Os palpites só podem ser vistos quando a rodada estiver fechada!", ephemeral=True)
            return
        
        palpites = palpites_banco.get_palpites_do_usuario(str(interaction.user.id))
        if not palpites:
            await interaction.response.send_message("Você não fez palpites na última rodada.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 Seus palpites da rodada anterior",
            color=get_sort_triples_color()
        )
        for mandante, visitante, palpite in palpites:
            simbolo = "🏠" if palpite == "1" else "⚖️" if palpite == "E" else "🚗"
            embed.add_field(name=f"{mandante} x {visitante}", value=f"Seu palpite: {simbolo} ({palpite})", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="📊 Mostra todos os palpites de um jogo")
    async def palpites_jogo(self, interaction: discord.Interaction, jogo_id: int):
        palpites = palpites_banco.get_palpites_do_jogo(jogo_id)
        if not palpites:
            await interaction.response.send_message("⚠️ Nenhum palpite registrado para esse jogo.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📋 Palpites do jogo {jogo_id}",
            color=discord.Color.blue()
        )
        for user_id, palpite in palpites:
            member = await interaction.guild.fetch_member(int(user_id))
            print(member)

            simbolo = "🏠" if palpite == "1" else "⚖️" if palpite == "E" else "🚗"
            embed.add_field(name=member.display_name, value=f"{simbolo} ({palpite})", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Palpite(bot))
