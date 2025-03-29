import os
import discord
from discord.ext import commands
from static.reactions import reactions
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    async def setup_reactions(self):
        channel_id = os.getenv('REACTIONS_CHANNEL_ID')
        message_id = os.getenv('REACTIONS_MESSAGE_ID')

        if not channel_id:
            return

        channel = self.bot.get_channel(int(channel_id))

        embed = discord.Embed(
            title=f'Reaja para ser marcado!',
            color=0xccff66
        )

        reaction_message = ""
        for reaction in reactions:
            reaction_message += f"{reaction['emoji']} para {reaction['description']} - !{reaction['command']}\n\n"

        embed.add_field(name="", value=reaction_message)

        allowed_emojis = {reaction['emoji'] for reaction in reactions}

        if message_id:
            message = await channel.fetch_message(int(message_id))

            await message.edit(embed=embed)

            for reaction in message.reactions:
                if str(reaction.emoji) not in allowed_emojis:
                    await reaction.clear()

            for reaction in reactions:
                await message.add_reaction(reaction['emoji'])

            return
        
        message = await channel.send(embed=embed)

        for reaction in reactions:
            await message.add_reaction(reaction['emoji'])
    
async def setup(bot):
    reaction_cog = Reaction(bot)
    await bot.add_cog(reaction_cog)
    await reaction_cog.setup_reactions()