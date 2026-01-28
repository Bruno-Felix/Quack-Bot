from datetime import datetime, timedelta
from .endpoints_cartola import request_market_close_date

async def market_close_date():
    rodada_atual, fechamento = await request_market_close_date()

    fechamento = datetime.fromtimestamp(fechamento['timestamp'])

    diferenca = fechamento - datetime.now()

    dias = diferenca.days
    horas, resto = divmod(diferenca.seconds, 3600)
    minutos, segundos = divmod(resto, 60)

    status_mercado = True if diferenca.total_seconds() > 0 else False

    diferenca_str = f'{dias} dias, {horas} horas e {minutos} minutos'
    fechamento_str = fechamento.strftime('%d/%m %H:%M')

    return rodada_atual, fechamento_str, status_mercado, diferenca_str, diferenca
