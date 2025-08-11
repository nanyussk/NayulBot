import discord
import json

from src import NayulCore
from src.utils.emojis import Emoji

class EditEmbed(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        self.children[7].disabled= True if len(embeds)==1 else False #Desabilita o botão caso tenha apenas um embed.
        self.embeds=embeds
        self.embed=embed
        self.items=items
    
    @discord.ui.button(label='Título', emoji=Emoji.paper, style=discord.ButtonStyle.gray, row=0)
    async def _title(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalTitle
        await inter.response.send_modal(ModalTitle(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Descrição', emoji=Emoji.annotation, style=discord.ButtonStyle.gray, row=0)
    async def _description(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalDescription
        await inter.response.send_modal(ModalDescription(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Cor', emoji=Emoji.paleta, style=discord.ButtonStyle.gray, row=0)
    async def _color(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.views import ColorView
        await inter.response.edit_message(view=ColorView(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Author', emoji=Emoji.icon_user, style=discord.ButtonStyle.gray, row=0)
    async def _author(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalAuthor
        await inter.response.send_modal(ModalAuthor(embeds=self.embeds, embed=self.embed))

    @discord.ui.button(label='Editar campos', emoji=Emoji.list, style=discord.ButtonStyle.gray, row=0)
    async def _fields(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.views import FieldsView
        await inter.response.edit_message(embeds=self.embeds, view=FieldsView(embeds=self.embeds, embed=self.embed))

    @discord.ui.button(label='Imagem/Thumbnail', emoji=Emoji.splash, style=discord.ButtonStyle.gray, row=1)
    async def _image(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalImageAndThumbnail
        await inter.response.send_modal(ModalImageAndThumbnail(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Rodapé', emoji=Emoji.footer, style=discord.ButtonStyle.gray, row=1)
    async def _footer(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalFooter
        await inter.response.send_modal(ModalFooter(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Remover Embed', emoji=Emoji.delete, style=discord.ButtonStyle.red, row=1)
    async def _remove_embed(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .main_panel import MainView
        self.embeds.remove(self.embed)
        await inter.response.edit_message(embeds=self.embeds, view=MainView(self.embeds))
    
    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=2)
    async def _back(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .main_panel import MainView
        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
    
    @discord.ui.button(label='Enviar JSON', emoji=Emoji.exportar, style=discord.ButtonStyle.blurple, row=2)
    async def _send_json(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalSendJSON
        await inter.response.send_modal(ModalSendJSON(embeds=self.embeds, embed=self.embed))

    @discord.ui.button(label='Obter JSON', emoji=Emoji.importar, style=discord.ButtonStyle.blurple, row=2)
    async def _get_json(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        embed_json = json.dumps(self.embed.to_dict(), ensure_ascii=True)
        await inter.response.send_message(f'```\n{embed_json}```', ephemeral=True)