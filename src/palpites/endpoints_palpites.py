import os
import requests


async def request_clubes_e_prox_rodada():
    results = requests.api.get('https://api.cartola.globo.com/partidas')
    results = results.json()

    jogos = extrair_jogos(results)

    return jogos

def extrair_jogos(json_data):
    partidas = json_data.get("partidas", [])
    
    return [
        {
            "partida_data": partida["partida_data"],
            "clube_casa_id": partida["clube_casa_id"],
            "clube_visitante_id": partida["clube_visitante_id"]
        }
        for partida in partidas
    ]
