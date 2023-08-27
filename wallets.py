import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from endpoint_requests import get_wallet
from utils.wallets_ids_list import wallet_ids_list

def get_all_wallets() -> list:
    all_objekts_list = []

    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_wallet, wallet_ids_list[wallet_owner]) for wallet_owner in wallet_ids_list]

            for future, wallet_owner in zip(futures, wallet_ids_list):
                wallet_response = future.result()

                final_wallet = __repair_wallet_objekts(wallet_response['objekts'], wallet_owner)

                all_objekts_list.extend(final_wallet)
                all_objekts_list.extend(__get_rest_of_wallet(wallet_response, wallet_owner))

        return pd.DataFrame(all_objekts_list)
    except Exception as error:
        raise Exception(f'Error on get all wallets: {error}')

def get_one_wallet(wallet_owner: str) -> list:
    wallet_objekts_list = []

    wallet_response = get_wallet(wallet_ids_list[wallet_owner])

    final_wallet = __repair_wallet_objekts(wallet_response['objekts'], wallet_owner)

    wallet_objekts_list.extend(final_wallet)
    wallet_objekts_list.extend(__get_rest_of_wallet(wallet_response, wallet_owner))

    return pd.DataFrame(wallet_objekts_list)

def __repair_wallet_objekts(wallet: list, wallet_owner: str):
    for objekt in wallet:
        objekt['owner'] = wallet_owner
        objekt['collection'] = int(objekt['collection'][:-1])

    return wallet

def __get_rest_of_wallet(wallet: object, wallet_owner: int) -> list:
    rest_of_wallet_objekts_list = []

    count_requests_wallet = 1
    aux_count = int(wallet['totalCount']) if wallet['totalCount'] else 100
    while aux_count > count_requests_wallet * 100:
        wallet_response = get_wallet(wallet_ids_list[wallet_owner], wallet['pageKey'])

        final_wallet = __repair_wallet_objekts(wallet_response['objekts'], wallet_owner)

        rest_of_wallet_objekts_list.extend(final_wallet)

        wallet = wallet_response
        count_requests_wallet += 1

    return rest_of_wallet_objekts_list
