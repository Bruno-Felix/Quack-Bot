async def get_users_by_reaction(self, emoji: str):
    channel_id = 1289335963138523197 # id do canal que ficará a mensagem para reagir
    message_id = 1355408693545402470 # id da mensagem

    channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
    msg = await channel.fetch_message(message_id)
    
    mentions = ""
    for reaction in msg.reactions:
        if(str(reaction.emoji) == emoji):
            users = [user async for user in reaction.users() if not user.bot]    
        
            if users:
                mentions += " ".join([f"<@{u.id}>" for u in users])

    return mentions
