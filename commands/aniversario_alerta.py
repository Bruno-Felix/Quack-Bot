from datetime import date, datetime, time, timezone, timedelta
import discord
from discord.ext import commands, tasks

brasil_tz = timezone(timedelta(hours=-3))

class AniversarioAlerta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aniversario_canal_id = 1147500370826895451
        self.check_aniversarios.start()
        super().__init__()

    def cog_unload(self):
        self.check_aniversarios.cancel()

    @tasks.loop(time=time(hour=21, minute=51, tzinfo=brasil_tz))  # Executa diariamente às 12:00
    async def check_aniversarios(self):
        now = datetime.now(brasil_tz)
        
        if self.aniversario_canal_id is None:
            print("Canal de aniversário não configurado.")
            return  # Canal não configurado
        
        aniversarios_csv = open('static/aniversarios.csv', 'r', encoding='utf-8')

        aniversarios = {}
        for line in aniversarios_csv:
            try:
                id, data = line.strip().split(',')
                aniversarios[id] = data
            except ValueError:
                print(f"Erro ao processar a linha: {line.strip()}")
                continue
        aniversarios_csv.close()

        channel = self.bot.get_channel(self.aniversario_canal_id)
        if channel is None:
            print(f"Canal com ID {self.aniversario_canal_id} não encontrado.")
            return  # Canal não encontrado

        today = date.today()
        today_str = today.strftime("%d/%m")
        aniversarios_xet = [id for id, data in aniversarios.items() if data == today_str]

        if aniversarios_xet:
            message = f"🎉 **Parabéns aos aniversariantes de hoje!** 🎉\n"
            message += "\n".join(f"- <@{id}>" for id in aniversarios_xet)
            await channel.send(message)
            await channel.send(file=discord.File("static/aniversario.gif"))
        else:
            print("Nenhum aniversário encontrado para hoje.")

    @check_aniversarios.before_loop
    async def before_check_aniversarios(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AniversarioAlerta(bot))