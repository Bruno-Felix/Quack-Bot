from ..requests import request_daily_kpop_calendar, request_weekly_kpop_calendar

async def get_daily_kpop_calendar(search_date):
    results = await request_daily_kpop_calendar(search_date)

    if not results:
        return 'Sem lançamentos hoje!!'
    else:
        response = '\n\n'.join(map(str, results))

    return response

async def get_weekly_kpop_calendar(search_start_date):
    results = await request_weekly_kpop_calendar(search_start_date)

    return results