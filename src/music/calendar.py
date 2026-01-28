import calendar
from datetime import datetime

from .endpoints_music import request_month_kpop_calendar

async def get_month_kpop_calendar():
    now = datetime.now()

    month = calendar.month_name[now.month].lower()
    year = now.year

    comebacks = await request_month_kpop_calendar(month, year)

    return comebacks