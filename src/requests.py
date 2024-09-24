import os
from notion_client import Client
from dotenv import load_dotenv

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

    return results