import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json
from pathlib import Path

from src.images import image_utils
from src.data.idols import idolList


TEMPLATES_PATH = Path(__file__).parent.parent / 'src' / 'data' / 'templates.json'

def load_templates():
    try:
        with TEMPLATES_PATH.open(encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


templates = load_templates()

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @app_commands.command(name='idols', description='O que o idol está mostrando?')
    async def idols(self, interaction: discord.Interaction, idol: idolList, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
        await interaction.response.defer()  
        
        image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

        if not image:
            await interaction.followup.send("Forneça uma imagem válida!")
            return

        template = templates.get('idols', {}).get(idol)
        if not template:
            await interaction.followup.send("Template do idol não encontrado.")
            return

        await image_utils.reply_image(interaction=interaction, template=template, image=image)


# --------------


async def setup(bot):
    await bot.add_cog(Images(bot))