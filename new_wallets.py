import pandas as pd
from utils.endpoint_requests import get_new_wallet
from utils.wallets_ids_list import wallet_ids_list

def get_one_wallet(wallet_owner: str) -> list:
    wallet_response = get_new_wallet()
    print('OK', len(wallet_response))

    """ final_wallet = __repair_wallet_objekts(wallet_response['objekts'], wallet_owner)

    wallet_objekts_list.extend(final_wallet)
    wallet_objekts_list.extend(__get_rest_of_wallet(wallet_response, wallet_owner))

    print(wallet_objekts_list) """

    list = __aux_new_list(wallet_response)

    return pd.DataFrame(list)

def __aux_new_list(wallet_list):
    new_list = []

    for objekt in wallet_list:
        obj = {}

        obj['transferrable'] = objekt['node']['transferrable']
        obj['member'] = objekt['node']['collection']['member']
        obj['number'] = objekt['node']['collection']['number'][:-1]
        obj['season'] = objekt['node']['collection']['season']

        new_list.append(obj)

    return new_list

def __repair_wallet_objekts(wallet: list, wallet_owner: str):
    for objekt in wallet:
        objekt['owner'] = wallet_owner
        objekt['collection'] = int(objekt['collection'][:-1])

    return wallet

def __get_rest_of_wallet(wallet: object, wallet_owner: int) -> list:
    rest_of_wallet_objekts_list = []

    count_requests_wallet = 1
    while int(wallet['totalCount']) > count_requests_wallet * 100:
        wallet_response = get_wallet(wallet_ids_list[wallet_owner], wallet['pageKey'])

        final_wallet = __repair_wallet_objekts(wallet_response['objekts'], wallet_owner)

        rest_of_wallet_objekts_list.extend(final_wallet)

        wallet = wallet_response
        count_requests_wallet += 1

    return rest_of_wallet_objekts_list