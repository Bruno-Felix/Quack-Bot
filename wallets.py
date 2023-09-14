import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from endpoint_requests import get_wallet
from utils.wallets_ids_list import wallet_ids_list
from utils.objekts import special_price, double_price, first_price

def get_all_wallets() -> list:
    all_objekts_list = []

    try:
        with ThreadPoolExecutor() as executor:
            print('get_all_wallets')
            futures = [executor.submit(get_wallet, wallet_ids_list[wallet_owner]) for wallet_owner in wallet_ids_list]

            for future, wallet_owner in zip(futures, wallet_ids_list):
                wallet_response = future.result()

                print(len(wallet_ids_list[wallet_owner]), wallet_owner)

                if len(wallet_response['objekts']) == 0:
                    wallet_response = get_wallet(wallet_ids_list[wallet_owner])

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

def read_wallet_price(wallet_owner: str) -> str:
    wallet_objekts_list = get_one_wallet(wallet_owner)

    price = 0
    special = 0
    double = 0
    first = 0

    for objekt in wallet_objekts_list.index:
        objekt_class = wallet_objekts_list['className'][objekt]
        objekt_is_transferable = wallet_objekts_list['transferable'][objekt]

        if objekt_is_transferable:
            if objekt_class == 'Special':
                price += special_price
                special += 1
            if objekt_class == 'Double':
                price += double_price
                double += 1
            if objekt_class == 'First':
                price += first_price
                first += 1

    print(special, double, first)
    return str(price), special, double, first

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
