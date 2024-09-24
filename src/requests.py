from notion_client import Client
from datetime import datetime, timedelta, date

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env na raiz do projeto
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_NOTION_ID = os.getenv('DATABASE_NOTION_ID')

async def request_daily_kpop_calendar(search_date):
    notion = Client(auth=NOTION_TOKEN)

    query = {
        "database_id": DATABASE_NOTION_ID,
        "filter": {
            "property": "Date",
            "date": {
                "equals": search_date
            }
        }
    }

    results = notion.databases.query(**query)

    return extract_music_names(results)

async def request_weekly_kpop_calendar(search_start_date):
    weekly_results = {}
    search_date = search_start_date
   
    for _ in range(7):
        results = await request_daily_kpop_calendar(search_date.strftime("%Y-%m-%d"))
        
        weekly_results[search_date.strftime("%Y-%m-%d")] = results

        search_date = search_date + timedelta(days=1)

    return weekly_results

def extract_music_names(results):
    music_names = []

    for page in results['results']:
        name_property = page['properties']['Name']['title']

        if name_property:
            title_text = ''.join(part['text']['content'] for part in name_property)
            music_names.append(title_text)

    return music_names