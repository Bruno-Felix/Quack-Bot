clubes_serie_a = [
    {"nome": "Mirassol", "abreviacao": "MIR", "id": 2305, "emoji": "<:time_mirassol:1466201647116976255>"},
    {"nome": "Flamengo", "abreviacao": "FLA", "id": 262, "emoji": "<:time_fla:1417997897588543498>"},
    {"nome": "Botafogo", "abreviacao": "BOT", "id": 263, "emoji": "<:time_botafogo:1466201161383153736>"},
    {"nome": "Corinthians", "abreviacao": "COR", "id": 264, "emoji": "<:time_corinthians:1419112044178968577>"},
    {"nome": "Bahia", "abreviacao": "BAH", "id": 265, "emoji": "<:time_bahia:1466201108325077013>"},
    {"nome": "Fluminense", "abreviacao": "FLU", "id": 266, "emoji": "<:time_flu:1418032651679432754>"},
    {"nome": "Vasco", "abreviacao": "VAS", "id": 267, "emoji": "<:time_vasco:1466201828453515410>"},
    {"nome": "Palmeiras", "abreviacao": "PAL", "id": 275, "emoji": "<:time_palmeiras:1417979275943870594>"},
    {"nome": "São Paulo", "abreviacao": "SAO", "id": 276, "emoji": "<:time_saopaulo:1466201764599566397>"},
    {"nome": "Santos", "abreviacao": "SAN", "id": 277, "emoji": "<:time_santos:1417984745869934784>"},
    {"nome": "Bragantino", "abreviacao": "RBB", "id": 280, "emoji": "<:time_braga:1466201239682420897>"},
    {"nome": "Atlético-MG", "abreviacao": "CAM", "id": 282, "emoji": "<:time_cam:1466201298008543272>"},
    {"nome": "Cruzeiro", "abreviacao": "CRU", "id": 283, "emoji": "<:time_cruzeiro:1466201538644152423>"},
    {"nome": "Grêmio", "abreviacao": "GRE", "id": 284, "emoji": "<:time_gremio:1466201595917373472>"},
    {"nome": "Internacional", "abreviacao": "INT", "id": 285, "emoji": "<:time_inter:1466176450158657546>"},
    {"nome": "Vitória", "abreviacao": "VIT", "id": 287, "emoji": ""},
    {"nome": "Athletico-PR", "abreviacao": "CAP", "id": 293, "emoji": "<:time_cap:1466201363074781285>"},
    {"nome": "Coritiba", "abreviacao": "CFC", "id": 294, "emoji": "<:time_coritiba:1466201483900096543>"},
    {"nome": "Chapecoense", "abreviacao": "CHA", "id": 315, "emoji": "<:time_chape:1466201424340844545>"},
    {"nome": "Remo", "abreviacao": "REM", "id": 364, "emoji": "<:time_remo:1466201707821137932>"},
]

def get_clubes_br_por_id(clube_id):
    return next((clube for clube in clubes_serie_a if str(clube["id"]) == clube_id), None)