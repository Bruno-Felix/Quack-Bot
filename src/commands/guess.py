import discord
import asyncio
import time
from random import randint
from discord.ext import commands
from discord import app_commands

from static.triples_colors import get_sort_triples_color

from ..guess.guess_idols import get_idol_guess_for_id, get_idol_guess_for_name, guess_idols_list
from ..guess.users import setup_users_database, daily_guess_reset
from ..guess.guess_logic import user_guess_action

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
        
        await interaction.response.send_message(f"{interaction.user.mention}\n{response}")

class Guess(commands.Cog):
    idol_of_the_day = None
    max_attempts_in_a_day = 20

    def __init__(self, bot):
        self.bot = bot

        setup_users_database()

        bot.loop.create_task(self.select_idol_guess_for_today())

        super().__init__()

    def get_random_idol():
        idol_of_the_day_id = randint(0, len(guess_idols_list) - 1)
        return get_idol_guess_for_id(idol_of_the_day_id)

    async def select_idol_guess_for_today(self):
        Guess.idol_of_the_day = Guess.get_random_idol()

        daily_guess_reset()

        print(Guess.idol_of_the_day)
    
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
        
        await ctx.send("Tente adivinhar o idol do dia:", view=view)

    @commands.command(name="gs")
    async def guess_row(self, ctx):
        bot = self.bot
        inicio = time.time()

        tempo_total = 60
        aviso_faltando = 20

        idol = Guess.get_random_idol()
        
        print(idol)

        altura = idol['height']
        ano_nascimento = idol['birthYear']
        type_idol = 'Homen' if idol['type'] == 'Boy' else 'Mulher'
        nacionalidade = idol['nationality']
        company = idol['company']

        embed = discord.Embed(
            title=f'Quack - Adivinhe o Idol',
            description='Você tem 1 minuto para acertar',
            color=get_sort_triples_color()
        )

        embed.add_field(name='Altura', value=f'{altura}', inline=True)
        embed.add_field(name='Nascimento', value=f'{ano_nascimento}', inline=True)
        if idol['type'] == 'Boy':
            embed.add_field(name='Nacionalidade', value=f'{nacionalidade}', inline=True)
        # embed.add_field(name='Tipo',value=f'{type_idol}', inline=True)
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

                if mensagem.content.lower() == idol['name'].lower():
                    await ctx.send(f"Parabéns {mensagem.author.mention}, você acertou!! 🎉\nA resposta correta era **{idol['name']} - {idol['group']}**")
                    
                    aviso_task.cancel()
                    
                    break
                else:
                    if mensagem.author != bot.user:
                        await mensagem.add_reaction("❌")

        except asyncio.TimeoutError:
            await ctx.send(f"Tempo acabou!! 🥺\nA resposta era **{idol['name']} - {idol['group']}**")

async def aviso_de_tempo(ctx, aviso_faltando, tempo_total):
    await asyncio.sleep(tempo_total - aviso_faltando)
    await ctx.send(f"Faltam apenas {aviso_faltando} segundos!")


# --------------


async def setup(bot):
    await bot.add_cog(Guess(bot))