import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

YOUTUBE_API = os.getenv('YOUTUBE_API')

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