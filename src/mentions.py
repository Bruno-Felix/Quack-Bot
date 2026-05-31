from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)

async def get_users_by_reaction(bot, channel_id, message_id, emoji: str):
    channel = await bot.fetch_channel(int(channel_id))
    message = await channel.fetch_message(int(message_id))
    
    mentions = ""
    for reaction in message.reactions:
        if(str(reaction.emoji) == emoji):
            users = [user async for user in reaction.users() if not user.bot]    
        
            if users:
                mentions += " ".join([f"<@{u.id}>" for u in users])

    return mentions