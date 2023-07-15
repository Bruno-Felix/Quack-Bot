import requests

def get_wallet(wallet_id, page_key = None):
    try:
        url = f'https://objekts.jinsoul.tv/api/objekts/{wallet_id}'
        url_page_key = f'?pageKey={page_key}' if page_key else ''

        resposta = requests.get(f'{url}{url_page_key}')

        if resposta.status_code != 200:
            raise Exception(f'Error on search wallet: {resposta.content}')
            
        return resposta.json()
    except Exception as error:
        raise error

def get_idol_photo(url_photo):
    try:
        resposta = requests.get(f'{url_photo}')

        if resposta.status_code != 200:
            raise Exception(f'Error on get idol photo')
            
        return resposta
    except Exception as error:
        raise error