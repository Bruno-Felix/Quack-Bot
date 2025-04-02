from datetime import date, datetime, time
import discord
from discord.ext import commands, tasks

class AniversarioAlerta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_channel_id = 551060445163945996
        self.check_birthdays.start()
        super().__init__()

    def cog_unload(self):
        self.check_birthdays.cancel()

    @tasks.loop(time=time(hour=15, minute=00))  # Executa diariamente às 12:00
    async def check_birthdays(self):
        now = datetime.now()
        
        if self.birthday_channel_id is None:
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

        channel = self.bot.get_channel(self.birthday_channel_id)
        if channel is None:
            print(f"Canal com ID {self.birthday_channel_id} não encontrado.")
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

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AniversarioAlerta(bot))