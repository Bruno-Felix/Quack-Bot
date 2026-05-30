import aiohttp

async def get_page_content(mes, dia):
    url = f'https://kpopping.com/categories/birthday/month/{mes}?day={dia}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception("Erro ao buscar os dados.")
            
            return await response.text()