from datetime import datetime, timedelta
from .endpoints_cartola import request_market_close_date
from zoneinfo import ZoneInfo

async def market_close_date():
    rodada_atual, fechamento = await request_market_close_date()

    fechamento = datetime.fromtimestamp(fechamento['timestamp'], tz=ZoneInfo("America/Sao_Paulo"))

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    diferenca = fechamento - agora

    dias = diferenca.days
    horas, resto = divmod(diferenca.seconds, 3600)
    minutos, segundos = divmod(resto, 60)

    status_mercado = diferenca.total_seconds() > 0

    diferenca_str = f'{dias} dias, {horas} horas e {minutos} minutos'
    fechamento_str = fechamento.strftime('%d/%m %H:%M')

    return rodada_atual, fechamento_str, status_mercado, diferenca_str, diferenca
