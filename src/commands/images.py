import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from random import randint

from src.images import image_utils
from src.data.templates import templates
from src.data.idols import idolList

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @app_commands.command(name='tohrcarteira', description='Tohr dando carteirada')
    async def tohrcarteira(self, interaction: discord.Interaction, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
        await interaction.response.defer()
        
        image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

        if not image:
            await interaction.followup.send("Forneça uma imagem válida!")
            return

        template = templates['tohr_carteira']

        await image_utils.reply_image(interaction=interaction, template=template, image=image)


    @app_commands.command(name='tohrreage', description='Tohr vai reagir')
    async def tohrreage(self, interaction: discord.Interaction, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
        await interaction.response.defer()

        image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

        if not image:
            await interaction.followup.send("Forneça uma imagem válida!")
            return

        template = templates['reacts'][randint(1, 4)]

        await image_utils.reply_image(interaction=interaction, template=template, image=image)


    @app_commands.command(name='idols', description='O que o idol está mostrando?')
    async def idols(self, interaction: discord.Interaction, idol: idolList, usuario: Optional[discord.Member] = None, imagem: Optional[discord.Attachment] = None):
        await interaction.response.defer()  
        
        image = await image_utils.get_image(interaction=interaction, member=usuario, image_attachment=imagem)

        if not image:
            await interaction.followup.send("Forneça uma imagem válida!")
            return

        template = templates['idols'][idol]

        await image_utils.reply_image(interaction=interaction, template=template, image=image)


# --------------


async def setup(bot):
    await bot.add_cog(Images(bot))