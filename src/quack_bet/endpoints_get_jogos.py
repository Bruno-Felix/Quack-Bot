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

def get_partidas_cartola():
    url = "https://api.cartola.globo.com/partidas"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    return response.json()

def get_lista_jogos():
    data = get_partidas_cartola()
    partidas = data.get("partidas", [])

    jogos = [
        {
            "partida_id": p["partida_id"],
            "partida_data": p["partida_data"],
            "clube_visitante_id": p["clube_visitante_id"],
            "clube_casa_id": p["clube_casa_id"],
        }
        for p in partidas
    ]

    return jogos