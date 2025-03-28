import os
from googleapiclient.discovery import build
from notion_client import Client
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_NOTION_ID = os.getenv('DATABASE_NOTION_ID')
YOUTUBE_API = os.getenv('YOUTUBE_API')

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

async def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API)

    response = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=1,
        type="video"
    ).execute()

    if response['items']:
        video = response['items'][0]
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        return video_url
    else:
        return "Nenhum vídeo encontrado"