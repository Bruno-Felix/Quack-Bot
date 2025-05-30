import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

async def get_users_by_reaction(self, channel_id, message_id, emoji: str):
    channel = await self.bot.fetch_channel(int(channel_id))
    message = await channel.fetch_message(int(message_id))
    
    mentions = ""
    for reaction in message.reactions:
        if(str(reaction.emoji) == emoji):
            users = [user async for user in reaction.users() if not user.bot]    
        
            if users:
                mentions += " ".join([f"<@{u.id}>" for u in users])

    return mentions