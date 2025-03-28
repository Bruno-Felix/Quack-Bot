import asyncio
import schedule


async def schedule_today_musics(bot):
    print('schedule sincronizado today_musics')
    music_cog = bot.get_cog("Music")

    schedule.every().day.at("11:00").do(lambda: asyncio.create_task(music_cog.hoje_diario()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(60)

async def schedule_change_idol_guess_for_today(bot):
    print('schedule sincronizado change_idol')
    guess_cog = bot.get_cog("Guess")

    schedule.every().day.at("03:00").do(lambda: asyncio.create_task(guess_cog.select_idol_guess_for_today()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)