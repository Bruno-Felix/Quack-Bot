import asyncio
import schedule

from src.quack_bet.quack_banco import get_jogos_postagem
from src.guess.guess_logic import select_idol_guess_for_today

async def scheduler_tasks(bot):
    print('---------\nSchedule Sincronizado!!\n---------')

    cartola_cog = bot.get_cog("Cartola")
    quack_bet_aposta_cog = bot.get_cog("QuackBetApostas")

    schedule.every().hour.at(":00").do(lambda: asyncio.create_task(cartola_cog.call_rodada_cartola()))

    schedule.every().day.at("03:00").do(lambda: asyncio.create_task(select_idol_guess_for_today()))
    schedule.every().day.at("15:00").do(lambda: asyncio.create_task(select_idol_guess_for_today()))
    schedule.every().day.at("21:00").do(lambda: asyncio.create_task(select_idol_guess_for_today()))
    
    #schedule.every().hour.at(":00").do(lambda: asyncio.create_task(quack_bet_aposta_cog.postar_jogos()))

    schedule.every().hour.at(":35").do(lambda: asyncio.create_task(quack_bet_aposta_cog.fechar_palpites()))
    #schedule.every().hour.at(":30").do(lambda: asyncio.create_task(quack_bet_aposta_cog.fechar_palpites()))


    while True:
        schedule.run_pending()
        await asyncio.sleep(1)