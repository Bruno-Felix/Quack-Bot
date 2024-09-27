from datetime import datetime
from ..endpoint_requests import request_market_close_date

async def market_close_date():
    rodada_atual, fechamento, status_mercado = await request_market_close_date()

    fechamento = datetime.fromtimestamp(fechamento['timestamp'])

    diferenca = fechamento - datetime.now()

    dias = diferenca.days
    horas, resto = divmod(diferenca.seconds, 3600)
    minutos, segundos = divmod(resto, 60)

    diferenca = f'{dias} dias, {horas} horas e {minutos} minutos'
    fechamento = fechamento.strftime('%d/%m/%Y %H:%M:%S')

    return rodada_atual, fechamento, status_mercado, diferenca
