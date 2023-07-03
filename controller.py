import requests
from models import Objekt
from data import lista_carteiras, url_site_carteira

def buscar_carteira(carteira_id):
    resposta = requests.get(
    f'https://polygon-mainnet.g.alchemy.com/nft/v2/OFnXkAWjmJ-emPdPy1fBsh-YVJgCo4MA/getNFTs?contractAddresses[]=0xA4B37bE40F7b231Ee9574c4b16b7DDb7EAcDC99B&contractAddresses[]=0x0fB69F54bA90f17578a59823E09e5a1f8F3FA200&owner={carteira_id}&withMetadata=true')

    return resposta.json()

def get_objekts_trocaveis(carteira, lista_objekts_trocaveis):
    resp_carteira = buscar_carteira(lista_carteiras[carteira])

    for objeck in resp_carteira['ownedNfts']:
        is_transferable = objeck['metadata']['objekt']['transferable']

        if is_transferable:
            novo_objekt = get_objekt_simplificado(objeck['metadata']['objekt'], carteira)
            lista_objekts_trocaveis.append(novo_objekt)

    return lista_objekts_trocaveis

def search_all_grid_in_lista_trocaveis(member, lista_objekts_trocaveis):
    lista_respostas = []
    inicio = 101

    for i in range(1, 17):
        lista_respostas = lista_respostas + search_objekts_in_lista_trocaveis(f'{member} {inicio}z', lista_objekts_trocaveis)
        inicio = inicio + 1

    return lista_respostas

def search_objekts_in_lista_trocaveis(busca_input, lista_objekts_trocaveis):
    lista_respostas = []
    achou = False

    for objeck in lista_objekts_trocaveis:
        if f'{objeck.member} {objeck.collectionNo}' == busca_input:
            achou = True
            lista_respostas.append(f'{objeck.collectionId}: {objeck.owner}')

    if achou == False:
        lista_respostas.append(f'{busca_input}: ninguem tem')

    return lista_respostas

def gerar_link_carteira(carteira):
    return url_site_carteira + lista_carteiras[carteira]

def get_objekt_simplificado(obj, owner):
    novo_objekt = Objekt(obj['collectionId'].lower(),
                        obj['season'].lower(),
                        obj['member'].lower(),
                        obj['collectionNo'].lower(),
                        obj['class'].lower(), 
                        obj['transferable'], 
                        owner)

    return novo_objekt