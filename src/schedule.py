import asyncio
import schedule

from src.guess.guess_logic import select_idol_guess_for_today

async def schedule_today_musics(bot):
    print('schedule sincronizado today_musics')
    music_cog = bot.get_cog("Music")

    schedule.every().day.at("11:00").do(lambda: asyncio.create_task(music_cog.hoje_diario()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(60)

async def schedule_change_idol_guess_for_today(bot):
    print('schedule sincronizado change_idol')

    schedule.every().day.at("03:00").do(lambda: asyncio.create_task(select_idol_guess_for_today()))
    schedule.every().day.at("15:00").do(lambda: asyncio.create_task(select_idol_guess_for_today()))
    schedule.every().day.at("21:00").do(lambda: asyncio.create_task(select_idol_guess_for_today()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)