import requests
from bs4 import BeautifulSoup
from datetime import date
import calendar
import re


def buscar_lancamentos(date):
    print('buscou')
    url = 'https://kpopofficial.com/kpop-comeback-schedule-may-2024/#15_May_2024'

    response = requests.get(url)

    if response.status_code == 200:
        # Parsing do conteúdo HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('td')
        
        lista_date = []

        capture_grupos = False
        for link in links:
            palavras = link.text.split()

            if palavras:
                if palavras[0] == calendar.month_name[date.month] and palavras[1] == str(date.day) + ',':
                    capture_grupos = True
                else:
                    if palavras[0] == calendar.month_name[date.month] and palavras[1] != str(date.day) + ',':
                        capture_grupos = False

                    if capture_grupos:
                        artista = ''
                        musica = ''
                        artista, musica = pegar_artista_e_musica(palavras)
                        string_sem_title = palavras[0]

                        if artista and musica:
                            lista_date.append(artista)
                            lista_date.append(musica)

        # Palavras a serem removidas
        palavras_a_remover = ['Kpop', 'KPOP', 'Song', 'Newest', '–', 'Navigation', 'Please']
        # Filtros na palavra
        substrings_a_remover = ['Title', 'MV Release', 'YouTube']

        lista_filtrada = []

        for palavra in lista_date:
            if palavra not in palavras_a_remover:
                palavra_a_inserir = palavra
                for substring in substrings_a_remover:
                    palavra_a_inserir = palavra_a_inserir.replace(substring, "")
                lista_filtrada.append(palavra_a_inserir)

        return lista_filtrada
    else:
        print("Falha ao fazer a requisição:", response.status_code)

def pegar_artista_e_musica(lista):

    # Convertendo a lista de palavras em uma string
    texto = ' '.join(lista)
    print('++++++++++++++++++++++')
    print(texto)
    print('?????????????????????')

    artista = ''
    musica = ''

    # Usando expressões regulares para extrair informações
    artista_match = re.search(r'(.*?)(Track:|April|May)', texto)
    musica_match = re.search(r'Track:(.*?)(Album:|Teaser:|Poster:|Video:)', texto)

    print('artista_match', artista_match)
    print('musica_match', musica_match)

    # Verificando se as informações foram encontradas
    if artista_match and musica_match:
        artista = artista_match.group(1).strip()
        musica = musica_match.group(1).strip()
        print("Artista:", artista)
        print("Música:", musica)
        print('----------------')


    return artista, musica