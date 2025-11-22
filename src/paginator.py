import discord
import asyncio

def split_text_by_newline(text: str, max_length: int) -> list[str]:
    pages = []
    text = text.strip()
    
    while len(text) > max_length:
        split_index = text.rfind("\n", 0, max_length)
        
        if split_index == -1:
            split_index = max_length
            
        pages.append(text[:split_index].strip())
        
        text = text[split_index:].lstrip()

    if text:
        pages.append(text)
        
    return [page for page in pages if page]

class PaginationView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, pages: list[str], title: str):
        super().__init__(timeout=180.0)
        self.pages = pages
        self.title = title
        self.total_pages = len(pages)
        self.current_page = 0
        self.requester_id = interaction.user.id
        self.original_interaction = interaction
        self.message = None

        if self.total_pages <= 1:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[2].disabled = True

    def get_embed(self) -> discord.Embed:
        page_content = self.pages[self.current_page]
        
        embed = discord.Embed(
            title=f'{self.title} (Página {self.current_page + 1}/{self.total_pages})',
            color=0xccff66
        )
        embed.description = page_content
        embed.set_footer(text=f"Solicitado por {self.original_interaction.user.display_name}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.requester_id:
            return True
        await interaction.response.send_message("Apenas o usuário que solicitou este menu pode interagir.", ephemeral=True)
        return False

    async def update_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % self.total_pages
        await self.update_page(interaction)

    @discord.ui.button(label="Próxima ➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % self.total_pages
        await self.update_page(interaction)

    @discord.ui.button(label="❌ Fechar", style=discord.ButtonStyle.danger)
    async def stop_pagination(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        try:
            await self.message.delete()
        except discord.NotFound:
            pass
        except discord.Forbidden:
            await interaction.response.edit_message(content="Paginação encerrada.", embed=None, view=None)
        
    async def on_timeout(self) -> None:
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

async def send_paginated_embeds(interaction: discord.Interaction, pages: list[str], title: str):
    if not pages:
        return

    view = PaginationView(interaction, pages, title)
    
    try:
        if view.total_pages == 1:
            await interaction.edit_original_response(embed=view.get_embed(), view=None)
        else:
            message = await interaction.edit_original_response(embed=view.get_embed(), view=view)
            view.message = message
            
    except discord.NotFound:
        print("Erro: A interação expirou ou foi deletada antes que o bot pudesse responder.")
    except Exception as e:
        print(f"Erro desconhecido ao enviar paginação: {e}")
