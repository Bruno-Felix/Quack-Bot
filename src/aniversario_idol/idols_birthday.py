from bs4 import BeautifulSoup
from datetime import datetime

from .endpoints_idols_birthday import get_page_content

async def aniversario_scraping(dia, mes):
    res = ""
    dia_selecionado = str(dia).zfill(2) if dia not in (None, "") else ""

    html = await get_page_content(mes, dia)

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('tbody tr')
    dia_atual = None

    for row in rows:
        columns = row.find_all('td')

        if len(columns) < 3:
            continue

        name_link = columns[0].find('a')
        if not name_link:
            continue

        idol = name_link.get_text(strip=True)

        group_text = columns[1].get_text(strip=True)
        grupo = "-" if group_text in {"", "-"} else group_text

        birthday_text = columns[2].get_text(strip=True)
        try:
            birthday_date = datetime.strptime(birthday_text, "%b %d, %Y")
        except ValueError:
            continue

        dia_aniversario = birthday_date.strftime("%d")

        if dia_selecionado and dia_selecionado != dia_aniversario:
            continue

        if not dia_selecionado and dia_atual != dia_aniversario:
            dia_atual = dia_aniversario
            res += f"\n**-- {dia_aniversario}/{mes} --**\n"

        if dia_selecionado and not res:
            res += f"{dia_selecionado}/{mes}\n\n"

        res += f'**{idol}** - {grupo} - {birthday_text}\n'

    return res if res else "Nenhum aniversário encontrado."