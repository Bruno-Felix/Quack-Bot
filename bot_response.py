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
            collection = idol_dt['collection'][ind]
            class_idol = 'A' if idol_dt['season'][ind] == 'Atom01' else 'B'
            string_idol += ' ' + class_idol + str(collection)

        response.append(idol + ': ' + string_idol)

    response = '\n'.join(map(str, response))
    
    return response