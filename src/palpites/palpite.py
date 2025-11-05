from datetime import datetime, timedelta
from .endpoints_palpites import request_market_close_date

async def market_close_date():
    rodada_atual, fechamento = await request_market_close_date()

    fechamento = datetime.fromtimestamp(fechamento['timestamp'])
    fechamento = fechamento - timedelta(hours = 3)

    diferenca = fechamento - datetime.now()

    dias = diferenca.days
    horas, resto = divmod(diferenca.seconds, 3600)
    minutos, segundos = divmod(resto, 60)

    status_mercado = True if diferenca.total_seconds() > 0 else False

    diferenca_str = f'{dias} dias, {horas} horas e {minutos} minutos'
    fechamento_str = fechamento.strftime('%d/%m/%Y %H:%M:%S')

    return rodada_atual, fechamento_str, status_mercado, diferenca_str, diferenca
