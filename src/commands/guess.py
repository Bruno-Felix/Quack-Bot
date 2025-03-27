import discord
from random import randint
from discord.ext import commands
from discord import app_commands

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

    async def select_idol_guess_for_today(self):
        idol_of_the_day_id = randint(0, len(guess_idols_list) - 1)
        Guess.idol_of_the_day = get_idol_guess_for_id(idol_of_the_day_id)

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


# --------------


async def setup(bot):
    await bot.add_cog(Guess(bot))