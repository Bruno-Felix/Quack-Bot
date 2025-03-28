import os
import requests


async def request_market_close_date():
    results = requests.api.get('https://api.cartola.globo.com/mercado/status')
    results = results.json()

    return results['rodada_atual'], results['fechamento']