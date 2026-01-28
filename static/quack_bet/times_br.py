clubes_serie_a = [
    {"nome": "Mirassol", "abreviacao": "MIR", "id": 2305, "emoji": ""},
    {"nome": "Flamengo", "abreviacao": "FLA", "id": 262, "emoji": "<:flamengo:1417997897588543498>"},
    {"nome": "Botafogo", "abreviacao": "BOT", "id": 263, "emoji": ""},
    {"nome": "Corinthians", "abreviacao": "COR", "id": 264, "emoji": "<:corinthians:1419112044178968577>"},
    {"nome": "Bahia", "abreviacao": "BAH", "id": 265, "emoji": ""},
    {"nome": "Fluminense", "abreviacao": "FLU", "id": 266, "emoji": "<:flu:1418032651679432754>"},
    {"nome": "Vasco", "abreviacao": "VAS", "id": 267, "emoji": ""},
    {"nome": "Palmeiras", "abreviacao": "PAL", "id": 275, "emoji": "<:palmeiras:1417979275943870594>"},
    {"nome": "São Paulo", "abreviacao": "SAO", "id": 276, "emoji": ""},
    {"nome": "Santos", "abreviacao": "SAN", "id": 277, "emoji": "<:santos:1417984745869934784>"},
    {"nome": "Bragantino", "abreviacao": "RBB", "id": 280, "emoji": ""},
    {"nome": "Atlético-MG", "abreviacao": "CAM", "id": 282, "emoji": ""},
    {"nome": "Cruzeiro", "abreviacao": "CRU", "id": 283, "emoji": ""},
    {"nome": "Grêmio", "abreviacao": "GRE", "id": 284, "emoji": ""},
    {"nome": "Internacional", "abreviacao": "INT", "id": 285, "emoji": ""},
    {"nome": "Vitória", "abreviacao": "VIT", "id": 287, "emoji": ""},
    {"nome": "Athletico-PR", "abreviacao": "CAP", "id": 293, "emoji": ""},
    {"nome": "Coritiba", "abreviacao": "CFC", "id": 294, "emoji": ""},
    {"nome": "Chapecoense", "abreviacao": "CHA", "id": 315, "emoji": ""},
    {"nome": "Remo", "abreviacao": "REM", "id": 364, "emoji": ""},
]

def get_clubes_br_por_id(clube_id):
    return next((clube for clube in clubes_serie_a if str(clube["id"]) == clube_id), None)