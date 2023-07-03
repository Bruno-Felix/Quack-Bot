import pyshorteners
from data import lista_carteiras, links_objekts
from controller import get_objekts_trocaveis, search_all_grid_in_lista_trocaveis, gerar_link_carteira

def buscar_objekts(busca_input):
    lista_objekts_trocaveis = []

    for carteira in lista_carteiras:      
        get_objekts_trocaveis(carteira, lista_objekts_trocaveis)

    return search_all_grid_in_lista_trocaveis(busca_input, lista_objekts_trocaveis)

def gerar_have_carteira(input):
    lista_objekts_trocaveis = []
    lista_resposta = []

    aa = get_objekts_trocaveis(input, lista_objekts_trocaveis)

    for a in aa:
        lista_resposta.append(f'{a.member} {a.collectionNo}')

    return lista_resposta

def gerar_lista_links_carteiras():
    lista_links_carteiras = []

    shorteners = pyshorteners.Shortener()

    for carteira in lista_carteiras:
        link = gerar_link_carteira(carteira)
        shorten_url = shorteners.tinyurl.short(link)

        lista_links_carteiras.append(carteira + ': ' + shorten_url)

    return lista_links_carteiras

def gerar_lista_links_objekts():
    lista_links_objekts = []

    shorteners = pyshorteners.Shortener()

    for lk in links_objekts:
        link = links_objekts[lk]
        shorten_url = shorteners.tinyurl.short(link)

        lista_links_objekts.append(lk + ': ' + shorten_url)

    return lista_links_objekts
