from utils.commands_strings import commands_idols

def criar_resposta_discord(lista):
    return '\n'.join(map(str, lista))

def resposta_buscar_objekts_integrante(lista_objekts1, lista_objekts2, lista_objekts3):
    resposta_grid1 = []
    resposta_grid2 = []
    resposta_grid3 = []

    if len(lista_objekts1) > 0:
        for ind in lista_objekts1.index:
            memberName = lista_objekts1['memberName'][ind]
            collection = lista_objekts1['collection'][ind]
            owner  = lista_objekts1['owner'][ind]

            info = f'{memberName} {collection}: {owner}'

            resposta_grid1.append(info)

        resposta_grid1 = '\n'.join(map(str, resposta_grid1))
    else:
        resposta_grid1 = '   -   '

    if len(lista_objekts2) > 0:
        for ind in lista_objekts2.index:
            memberName = lista_objekts2['memberName'][ind]
            collection = lista_objekts2['collection'][ind]
            owner  = lista_objekts2['owner'][ind]
            
            info = f'{memberName} {collection}: {owner}'

            resposta_grid2.append(info)
        
        resposta_grid2 = '\n'.join(map(str, resposta_grid2))
    else:
        resposta_grid2 = '   -   '

    if len(lista_objekts3) > 0:
        for ind in lista_objekts3.index:
            memberName = lista_objekts3['memberName'][ind]
            collection = lista_objekts3['collection'][ind]
            owner  = lista_objekts3['owner'][ind]
            
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
            collection = idol_dt['collection'][ind]
            class_idol = 'A' if idol_dt['season'][ind] == 'Atom01' else 'B'
            string_idol += ' ' + class_idol + str(collection)

        response.append(idol + ': ' + string_idol)

    response = '\n'.join(map(str, response))
    
    return response