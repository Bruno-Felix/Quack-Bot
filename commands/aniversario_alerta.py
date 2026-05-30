from datetime import date, datetime, time, timezone, timedelta
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from pathlib import Path

from src.aniversario_bobo.aniversario_banco import (
    listar_aniversarios,
    setup_aniversario_database,
)

dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)

brasil_tz = timezone(timedelta(hours=-3))

# --------- HORÁRIO DA EXECUÇÃO ---------
hour = 11
minute = 0

class AniversarioAlerta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aniversario_canal_id = int(os.getenv('QUACK_BOT_BIRTHDAY_CHANNEL_ID'))
        setup_aniversario_database()
        self.check_aniversarios.start()
        super().__init__()

    def cog_unload(self):
        self.check_aniversarios.cancel()

    @tasks.loop(time=time(hour=hour, minute=minute, tzinfo=brasil_tz))  # Executa diariamente às 11:00
    async def check_aniversarios(self):
        now = datetime.now(brasil_tz)
        
        if self.aniversario_canal_id is None:
            print("Canal de aniversário não configurado.")
            return  # Canal não configurado

        aniversarios = await listar_aniversarios()

        channel = self.bot.get_channel(self.aniversario_canal_id)
        if channel is None:
            print(f"Canal com ID {self.aniversario_canal_id} não encontrado.")
            return  # Canal não encontrado

        today = date.today()
        today_str = today.strftime("%d/%m")
        aniversarios_bobo = [id for id, data in aniversarios if data == today_str]

        if aniversarios_bobo:
            mentions = []
            for user_id in aniversarios_bobo:
                user = self.bot.get_user(int(user_id))
                if user:
                    mentions.append(user.mention)

            mentions_str = ", ".join(mentions)
            file=discord.File("static/aniversario.gif")
            embed = discord.Embed(
                title="🎉 Aniversariantes do dia! 🎂",
                description=f"Hoje é aniversário de {mentions_str}! Parabéns! 🎂",
                color=discord.Color.gold(),
            )
            await channel.send(embed=embed, file=file)
        else:
            print("Nenhum aniversário encontrado para hoje.")

    @check_aniversarios.before_loop
    async def before_check_aniversarios(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AniversarioAlerta(bot))