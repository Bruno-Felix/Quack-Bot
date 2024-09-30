import io
from typing import Optional
import discord

from src.images import image_generator

async def get_image(interaction: discord.Interaction, member: Optional[discord.Member] = None, image_attachment: Optional[discord.Attachment] = None):
    image = None
    if member == None and image_attachment == None: 
        messages = interaction.channel.history(limit=15)

        async for message in messages:            
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        image = attachment
                        break
                if image:
                    break
    elif member and member.avatar:
        image = member.avatar
    elif image_attachment and image_generator.is_image(image_attachment.filename):
        image = image_attachment

    return image
    
async def reply_image(interaction, template, image):
    result = image_generator.make_image(template, image)
    
    with io.BytesIO() as image_binary:
        result.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.followup.send(file=discord.File(fp=image_binary, filename='image.png'))
        image_binary.close()
