from utils.commands_strings import commands_idols

def criar_resposta_discord(lista):
    return '\n'.join(map(str, lista))

def response_bot_search_idol_objekts(grid_1, grid_2, grid_3):
    resposta_grid1 = []
    resposta_grid2 = []
    resposta_grid3 = []

    if len(grid_1) > 0:
        for ind in grid_1.index:
            memberName = grid_1['memberName'][ind]
            collection = grid_1['collection'][ind]
            owner  = grid_1['owner'][ind]

            info = f'{memberName} {collection}: {owner}'

            resposta_grid1.append(info)

        resposta_grid1 = '\n'.join(map(str, resposta_grid1))
    else:
        resposta_grid1 = '   -   '

    if len(grid_2) > 0:
        for ind in grid_2.index:
            memberName = grid_2['memberName'][ind]
            collection = grid_2['collection'][ind]
            owner  = grid_2['owner'][ind]
            
            info = f'{memberName} {collection}: {owner}'

            resposta_grid2.append(info)
        
        resposta_grid2 = '\n'.join(map(str, resposta_grid2))
    else:
        resposta_grid2 = '   -   '

    if len(grid_3) > 0:
        for ind in grid_3.index:
            memberName = grid_3['memberName'][ind]
            collection = grid_3['collection'][ind]
            owner  = grid_3['owner'][ind]
            
            info = f'{memberName} {collection}: {owner}'

            resposta_grid3.append(info)
        
        resposta_grid3 = '\n'.join(map(str, resposta_grid3))
    else:
        resposta_grid3 = '   -   '

    return resposta_grid1, resposta_grid2, resposta_grid3

def response_bot_wallet_by_idol(array_wallet):
    response = []

    for idol in commands_idols:
        if len(array_wallet[idol]) == 0:
            continue
        
        idol_dt = array_wallet[idol]

        string_idol = ''
        for ind in idol_dt.index:
            collection = idol_dt['number'][ind]
            class_idol = __aux_take_season(idol_dt['season'][ind])
            string_idol += ' ' + class_idol + str(collection)

        response.append(idol + ': ' + string_idol)

    response = '\n'.join(map(str, response))
    
    return response

def __aux_take_season(season):
    if season == 'Atom01':
        return 'A'
    
    if season == 'Binary01':
        return 'B'
    
    if season == 'Cream01':
        return 'C'
    
def criar_resposta_discord_musicas(lista):
    print(lista)
    # Inicializar uma lista vazia para armazenar os pares de palavras
    pares_palavras = []

    if not lista:
        return 'Sem lançamentos nessa data.\n'

    # Iterar sobre a lista de palavras em passos de 2
    for i in range(0, len(lista), 2):
        # Verificar se ainda existem duas palavras consecutivas
        if i + 1 < len(lista):
            # Juntar duas palavras consecutivas e adicionar à lista de pares de palavras
            par = lista[i] + '-> ' + lista[i + 1]
            pares_palavras.append(par)
        else:
            # Se houver um número ímpar de palavras na lista, adicionar a última palavra individualmente
            pares_palavras.append(lista[i])

    # Juntar os pares de palavras com '\n' e retornar como uma única string
    return '\n\n'.join(pares_palavras)