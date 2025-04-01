import discord
import asyncio
import time
from discord.ext import commands
from discord import app_commands

from static.triples_colors import get_sort_triples_color

from src.guess.users import setup_users_database
from src.guess.guess_logic import user_guess_action, select_idol_guess_for_today, get_random_idol, get_groups_by_company

class GuessModal(discord.ui.Modal, title="Adivinhe o Idol!"):
    idol_name = discord.ui.TextInput(
        label="Digite o nome do idol:",
        placeholder="Exemplo: Jungkook",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        idol_name = self.idol_name.value
        
        response = user_guess_action(str(user_id), idol_name)

        if response == 1:
            embed_correct = discord.Embed(
                title=f"Parabéns!!",
                description=f"Você já acertou hoje 🎉",
                color=get_sort_triples_color()
            )

            await interaction.response.send_message(embed=embed_correct)
        elif response == 2:
            embed_correct = discord.Embed(
                title=f"Você Acertou!!",
                description=f"Parabéns {interaction.user.mention} 🎉\nVocê cravou o idol do dia",
                color=get_sort_triples_color()
            )

            await interaction.response.send_message(embed=embed_correct)
        else:
            button = discord.ui.Button(label="Tentar outra vez", style=discord.ButtonStyle.primary)
            button_list_groups = discord.ui.Button(label="Ver lista de grupos", style=discord.ButtonStyle.secondary)

            async def button_callback(interaction: discord.Interaction):
                await interaction.response.send_modal(GuessModal())
        
            async def button_list_callback(interaction: discord.Interaction):
                group_data = get_groups_by_company()
                group_list_message = "\n".join([f"**{company}** - " + ", ".join(groups) for company, groups in group_data.items()])

                await interaction.response.send_message(f"Lista de Grupos:\n\n{group_list_message}", ephemeral=True)
        
            button.callback = button_callback
            button_list_groups.callback = button_list_callback
            
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button_list_groups)

            await interaction.response.send_message(f"{interaction.user.mention}\n{response}", ephemeral=True, view=view)

class Guess(commands.Cog):
    have_guess_game_open = False
    idol_of_the_day = None
    streak_ranking = {}
    max_attempts_in_a_day = 15

    def __init__(self, bot):
        self.bot = bot

        setup_users_database()

        bot.loop.create_task(select_idol_guess_for_today())

        super().__init__()

    
    @app_commands.command(name="guess_idol", description="Adivinhe o idol do dia!")
    async def guess_idol(self, interaction: discord.Interaction):
        """Abre um pop-up para o usuário digitar a resposta"""
        await interaction.response.send_modal(GuessModal())

    @commands.command(name="guess")
    async def guess(self, ctx):
        button = discord.ui.Button(label="Adivinhar", style=discord.ButtonStyle.primary)
        
        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(GuessModal())
        
        button.callback = button_callback
        view = discord.ui.View()
        view.add_item(button)
        
        embed = discord.Embed(
            title=f'Quack - Adivinhe o Idol do Dia',
            description=f'Tente adivinhar o **idol do dia**!!\n\nInsira o **nome** do idol que acredita ser\nVocê tem {Guess.max_attempts_in_a_day} tentativas, **Faça seu palpite** 😆',
            color=get_sort_triples_color()
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name="gs")
    async def guess_row(self, ctx):
        bot = self.bot
        tempo_total = 60
        aviso_faltando = 20
        tempo_espera = 10

        if Guess.have_guess_game_open:
            await ctx.send(f"Já tem um jogo aberto, {ctx.author.mention}.")
            return

        Guess.have_guess_game_open = True

        while True:
            inicio = time.time()
            alguem_tentou = False

            idol = get_random_idol()

            altura = f"{idol['height']} cm" if idol['height'] else 'Sem altura declarada'
            ano_nascimento = idol['birthYear']
            nacionalidade = idol['nationality']
            company = idol['company']

            embed = discord.Embed(
                title=f'Quack - Adivinhe o Idol',
                description='Tem **1 minuto** para acertar\n\nEscreva no chat o **nome** do idol que acredita ser\n**Faça seu palpite** 😆',
                color=get_sort_triples_color()
            )

            embed.add_field(name='Altura', value=f'{altura}', inline=True)
            embed.add_field(name='Nascimento', value=f'{ano_nascimento}', inline=True)
            embed.add_field(name='Nacionalidade', value=f'{nacionalidade}', inline=True)
            embed.add_field(name='Empresa', value=f'{company}', inline=True)
            
            await ctx.send(embed=embed)

            def check(m):
                return m.channel == ctx.channel

            aviso_task = asyncio.create_task(aviso_de_tempo(ctx, aviso_faltando, tempo_total))

            try:
                while True:
                    tempo_passado = time.time() - inicio
                    tempo_restante = tempo_total - tempo_passado

                    if tempo_restante <= 0:
                        raise asyncio.TimeoutError
                    
                    mensagem = await bot.wait_for("message", timeout=tempo_restante, check=check)

                    if mensagem.author != bot.user:
                        alguem_tentou = True
                    
                    if mensagem.content.lower() == idol['name'].lower():
                        await mensagem.add_reaction("✅")

                        Guess.streak_ranking[mensagem.author] = Guess.streak_ranking.get(mensagem.author, 0) + 1
                        
                        embed_correct = discord.Embed(
                            title=f"Você Acertou!!",
                            description=f"Parabéns {mensagem.author.mention}\nA resposta correta era **{idol['name']} - {idol['group']}**",
                            color=get_sort_triples_color()
                        )
                        
                        await ctx.send(embed=embed_correct)
                        
                        aviso_task.cancel()
                        break
                    else:
                        if mensagem.author != bot.user:
                            await mensagem.add_reaction("❌")
            except asyncio.TimeoutError:
                embed_wrong = discord.Embed(
                    title=f"Tempo acabou!!",
                    description=f"A resposta era **{idol['name']} - {idol['group']}**",
                    color=get_sort_triples_color()
                )
                await ctx.send(embed=embed_wrong)

            if Guess.streak_ranking:
                ranking_embed = discord.Embed(
                    title="Streak 🏆",
                    description="Uma nova rodada comecará em breve..." if alguem_tentou else "Resultado final",
                    color=get_sort_triples_color()
                )

                for user, acertos in sorted(Guess.streak_ranking.items(), key=lambda x: x[1], reverse=True):
                    ranking_embed.add_field(name=user.name, value=f"{acertos} acertos", inline=False)
                
                await ctx.send(embed=ranking_embed)
            
            await asyncio.sleep(tempo_espera) # Esperar antes de reiniciar
            
            if not alguem_tentou:
                Guess.streak_ranking.clear()
                Guess.have_guess_game_open = False
                
                break

async def aviso_de_tempo(ctx, aviso_faltando, tempo_total):
    await asyncio.sleep(tempo_total - aviso_faltando)
    await ctx.send(f"Faltam apenas {aviso_faltando} segundos!")


# --------------


async def setup(bot):
    await bot.add_cog(Guess(bot))