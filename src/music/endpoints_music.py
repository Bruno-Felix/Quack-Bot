import requests
from bs4 import BeautifulSoup

async def request_month_kpop_calendar(month, year):
    URL = f"https://kpopofficial.com/kpop-comeback-schedule-{month}-{year}/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    comebacks = []

    ul = soup.select_one("ul.wp-block-post-template")

    if not ul:
        raise Exception("Lista de comebacks não encontrada")

    for li in ul.select("li"):
        values = [v.get_text(strip=True) for v in li.select(".gspb_meta_value")]

        if len(values) < 4:
            continue

        comeback = {
            "month": values[0],
            "date": values[1],
            "title": values[2],
            "album": values[3],
            "views": values[4] if len(values) >= 5 else None
        }

        comebacks.append(comeback)

    return comebacks