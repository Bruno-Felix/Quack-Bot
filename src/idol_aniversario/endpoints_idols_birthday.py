import aiohttp

async def get_page_content(mes):
    url = f'https://kpopping.com/calendar/2024-{mes}/category-Birthday'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception("Erro ao buscar os dados.")
            
            return await response.text()