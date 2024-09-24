import requests

url = "https://squid.subsquid.io/cosmo/graphql"

def generate_query():
    id = '0xa446932803BC8a80d87b546732eDF7c51AC264B7'
    return f"""
    query MyQuery {{
        objektsConnection(orderBy: received_DESC, first: 2000, where: {{owner_eq: "{id}", collection: {{class_eq: "First"}}, transferrable_eq: true}}) {{
            edges {{
                node {{
                    id
                    transferrable
                    minted
                    collection {{
                        member
                        number
                        season
                    }}
                }}
            }}
        }}
    }}
    """

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
    
def get_new_wallet():
    data = {'query': generate_query()}
    resposta = requests.post(url, json=data)

    if resposta.status_code != 200:
        raise Exception(f'Error on search wallet: {resposta.content}')
    
    data = resposta.json()
    
    return data['data']['objektsConnection']['edges']