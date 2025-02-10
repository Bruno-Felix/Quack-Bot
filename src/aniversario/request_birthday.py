import aiohttp
from bs4 import BeautifulSoup


async def aniversario_scraping(dia, mes):

    if dia:
        dia = str(dia).zfill(2)
    mes = str(mes).zfill(2)

    res = ""

    url = f'https://kpopping.com/calendar/2024-{mes}/category-Birthday'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
            else:
                return "Erro ao buscar os dados."

    soup = BeautifulSoup(html, 'html.parser')

    days = soup.find_all('div', class_='day')


    for day in days:

        elements = day.find_all(['h2', 'a', 'span'])

        for n2, event in enumerate(elements):

            if n2 == 0:
                dia_aniversario = event.text.split(",")[0][3:].strip().zfill(2)
                if dia == "":
                    res += f"\n**-- {dia_aniversario}/{mes} --**\n"
                elif dia == dia_aniversario:
                    res += f"{dia}/{mes}\n\n"

            elif event.name == 'a' and "idol" in event['href'] and "picture" not in str(event):
                if "Turns" in event.text:
                    idol = event.text.split("Turns")[0].strip()
                else:
                    idol = event.text

            elif event.name == 'span' and "Birthday" not in event.text:
                if "Turns" in event.text:
                    idade = event.text.split("Turns")[1].strip()
                else:
                    idade = event.text

            elif event.name == 'a' and "group" in event['href']:
                grupo = event.text
                if dia == "":
                    res += f'**{idol}** ({idade} anos) - {grupo}\n'
                elif dia == dia_aniversario:
                    res += f'**{idol}** ({idade} anos) - {grupo}\n'
    return res if res else "Nenhum aniversário encontrado."