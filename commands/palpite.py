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
        await interaction.response.defer(ephemeral=True)
        ultima_rodada = palpites_banco.pegar_ultima_rodada()

        if not ultima_rodada:
            prox_id = 1
            palpites_banco.criar_rodada(prox_id)
            await interaction.followup.send(f"✅ Rodada {prox_id} criada!")
            return
        
        if ultima_rodada[2]:
            await interaction.followup.send("⚠️ Já existe uma rodada aberta!")
            return
        
        prox_id = ultima_rodada[0] + 1
        palpites_banco.criar_rodada(prox_id)
        await interaction.followup.send(f"✅ Rodada {prox_id} criada!")
      
        jogos = await endpoints_palpites.request_clubes_e_prox_rodada()
        for partida in jogos:
            casa = get_team_by_id(partida['clube_casa_id'])
            visitante = get_team_by_id(partida['clube_visitante_id'])

            jogo_id = palpites_banco.inserir_jogo(
                prox_id,
                casa['nome_fantasia'],
                visitante['nome_fantasia'],
                partida['partida_data']
            )

            msg = await interaction.channel.send(
                f"**{casa['nome_fantasia']} x {visitante['nome_fantasia']}**\n"
                f"🕒 {partida['partida_data']}\n\n"
                "Reaja com:\n"
                "1️⃣ Mandante vence\n"
                "🇪 Empate\n"
                "2️⃣ Visitante vence"
            )

            for emoji in ["1️⃣", "🇪", "2️⃣"]:
                await msg.add_reaction(emoji)

            palpites_banco.atualizar_message_id(jogo_id, msg.id)

        await interaction.followup.send("✅ Nova rodada criada!")


    @app_commands.command(description="🔒 Fecha a rodada atual e salva os palpites")
    async def fechar_rodada(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        palpites_banco.listar_todos_os_jogos()
        palpites_banco.listar_rodadas()

        rodada_id = palpites_banco.fechar_rodada()
      
        if not rodada_id:
            await interaction.followup.send("⚠️ Não há rodada aberta.")
            return

        jogos = palpites_banco.get_jogos_da_rodada(rodada_id)
        if not jogos:
            await interaction.followup.send("❌ Nenhum jogo encontrado para essa rodada.")
            return

        channel = interaction.channel

        print('--------------------Salvando jogos', len(jogos))
        for jogo_id, message_id in jogos:
            print('Jogo -', jogo_id)
            if not message_id:
                print(f"❌ Jogo {jogo_id} não tem message_id definido, pulando...")
                continue

            try:
                message = await channel.fetch_message(int(message_id))
            except Exception as e:
                print(f"Erro ao buscar mensagem {message_id}: {e}")
                continue

            votos = {}

            for reaction in message.reactions:
                if str(reaction.emoji) not in ["1️⃣", "🇪", "2️⃣"]:
                    continue

                async for user in reaction.users():
                    if user.bot:
                        continue
                    if user.id not in votos:
                        votos[user.id] = []
                    votos[user.id].append(str(reaction.emoji))

            for user_id, emojis in votos.items():
                if len(emojis) != 1:
                    print(f"Usuário {user_id} reagiu mais de uma vez, ignorando palpites.")
                    continue

                emoji = emojis[0]
                palpite = "1" if emoji == "1️⃣" else "E" if emoji == "🇪" else "2"
                palpites_banco.salvar_palpite(str(user_id), jogo_id, palpite)

        await interaction.followup.send(f"🔒 Rodada {rodada_id} foi fechada! Todos os palpites foram salvos.")


    @app_commands.command(description="📊 Mostra seus palpites da última rodada")
    async def meus_palpites(self, interaction: discord.Interaction):
        palpites_banco.listar_todos_os_jogos()

        ultima_rodada = palpites_banco.pegar_ultima_rodada()
        print('rodada id', ultima_rodada)
        if not ultima_rodada:
            await interaction.response.send_message(
                "⚠️ Não existe rodada para mostrar palpites!"
            )
            return

        palpites = palpites_banco.get_palpites_do_usuario(str(interaction.user.id))
        if not palpites:
            await interaction.response.send_message(
                "Você não fez palpites na última rodada."
            )
            return

        embed = discord.Embed(
            title=f"📋 Seus palpites",
            color=get_sort_triples_color()
        )

        for mandante, visitante, palpite, jogo_id in palpites:
            simbolo = "🏠 Mandante" if palpite == "1" else "Empate" if palpite == "E" else "🚗 Visitante"

            resultado = palpites_banco.get_resultado_jogo(jogo_id)
            status = ""
            if resultado:
                status = " ✅" if palpite == resultado else " ❌"

            embed.add_field(
                name=f"{mandante} x {visitante}",
                value=f"Seu palpite: {simbolo} {status}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(description="📊 Mostra todos os palpites de um jogo")
    async def palpites_jogo(self, interaction: discord.Interaction, jogo_id: int):
        await interaction.response.defer()

        palpites = palpites_banco.get_palpites_do_jogo(jogo_id)
        if not palpites:
            await interaction.followup.send("⚠️ Nenhum palpite registrado para esse jogo.")
            return
    
        # Busca o resultado do jogo
        resultado = palpites_banco.get_resultado_jogo(jogo_id)
    
        embed = discord.Embed(
            title=f"📋 Palpites do jogo {jogo_id}",
            color=discord.Color.blue()
        )
    
        for user_id, palpite in palpites:
            try:
                member = await interaction.guild.fetch_member(int(user_id))
                nome = member.display_name
            except:
                nome = f"User {user_id}"
    
            simbolo = "🏠" if palpite == "1" else "⚖️" if palpite == "E" else "🚗"
            status = ""
            if resultado:  # se já tem resultado
                status = " ✅" if palpite == resultado else " ❌"
    
            embed.add_field(name=nome, value=f"{simbolo} ({palpite}){status}", inline=False)
    
        await interaction.followup.send(embed=embed)


    @app_commands.command(description="🏆 Define o vencedor de um jogo")
    @app_commands.describe(jogo_id="ID do jogo", resultado="Resultado: 1 = mandante, E = empate, 2 = visitante")
    async def resultado_jogo(self, interaction: discord.Interaction, jogo_id: int, resultado: str):
        if resultado not in ["1", "E", "2"]:
            await interaction.response.send_message("⚠️ Resultado inválido! Use 1, E ou 2.")
            return

        palpites_banco.definir_resultado(jogo_id, resultado)
        await interaction.response.send_message(f"✅ Resultado do jogo {jogo_id} registrado como `{resultado}`.")
        

    @app_commands.command(description="🏆 Fecha resultados da rodada e atribui pontos")
    async def fechar_resultados(self, interaction: discord.Interaction):
        rodada = palpites_banco.get_rodada_aberta()
        if rodada:
            await interaction.response.send_message(
                "⚠️ Não é possível fechar resultados enquanto a rodada está aberta."
            )
            return

        rodada_fechada = palpites_banco.get_ultima_rodada_fechada()

        if not rodada_fechada:
            await interaction.response.send_message("⚠️ Nenhuma rodada para fechar resultados.")
            return

        rodada_id = rodada_fechada[0]

        msg = palpites_banco.atribuir_pontos_rodada(rodada_id)
        await interaction.response.send_message(f"✅ {msg}")


    @app_commands.command(description="🏆 Mostra o ranking de pontos dos usuários")
    async def ranking(self, interaction: discord.Interaction):
        usuarios = palpites_banco.get_ranking()
    
        if not usuarios:
            await interaction.response.send_message("⚠️ Nenhum usuário com pontos registrado.")
            return
    
        mensagem = "**🏆 Ranking de Pontos**\n\n"
        for i, (user_id, pontos) in enumerate(usuarios, start=1):
            member = interaction.guild.get_member(int(user_id))
            nome = member.display_name if member else f"<@{user_id}>"
            mensagem += f"**{i}º** - {nome}: `{pontos} ponto(s)`\n"
    
        await interaction.response.send_message(mensagem)

    @app_commands.command(description="➕ Adiciona pontos manualmente a um jogador")
    @app_commands.describe(user_id="ID do usuário alvo", pontos="Quantidade de pontos a adicionar")
    async def add_pontos(self, interaction: discord.Interaction, user_id: str, pontos: int):
        # Verifica se quem executou o comando é você
        if interaction.user.id != 701955314161025086:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
            return

        # Atualiza os pontos no banco usando a função
        try:
            palpites_banco.atualizar_pontos_usuario(user_id, pontos)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Erro ao adicionar pontos: `{e}`", ephemeral=True)
            return

        # Obtém nome do usuário no servidor
        try:
            member = await interaction.guild.fetch_member(int(user_id))
            nome = member.display_name
        except:
            nome = f"ID: {user_id}"

        await interaction.response.send_message(f"🏅 `{pontos}` pontos adicionados para **{nome}({user_id})**!")




async def setup(bot):
    await bot.add_cog(Palpite(bot))
