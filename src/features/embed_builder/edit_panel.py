import discord
import json
import logging

from src import NayulCore
from src.utils.emojis import Emoji

log = logging.getLogger(__name__)

class EditEmbed(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        # Disable remove button when there is only one embed.
        self.children[7].disabled = len(embeds) <= 1
        self.embeds=embeds
        self.embed=embed
        self.items=items
        log.debug('EditEmbed iniciado embeds=%s', len(embeds))
    
    @discord.ui.button(label='Título', emoji=Emoji.paper, style=discord.ButtonStyle.gray, row=0)
    async def _title(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalTitle
        log.debug('Abrindo modal titulo embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalTitle(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Descrição', emoji=Emoji.annotation, style=discord.ButtonStyle.gray, row=0)
    async def _description(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalDescription
        log.debug('Abrindo modal descricao embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalDescription(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Cor', emoji=Emoji.paleta, style=discord.ButtonStyle.gray, row=0)
    async def _color(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.views import ColorView
        log.debug('Abrindo seletor de cor embed_builder user_id=%s', inter.user.id)
        await inter.response.edit_message(view=ColorView(embeds=self.embeds, embed=self.embed, items=self.items))
    
    @discord.ui.button(label='Author', emoji=Emoji.icon_user, style=discord.ButtonStyle.gray, row=0)
    async def _author(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalAuthor
        log.debug('Abrindo modal autor embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalAuthor(embeds=self.embeds, embed=self.embed))

    @discord.ui.button(label='Editar campos', emoji=Emoji.list, style=discord.ButtonStyle.gray, row=0)
    async def _fields(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.views import FieldsView
        log.debug('Abrindo editor de campos embed_builder user_id=%s', inter.user.id)
        await inter.response.edit_message(embeds=self.embeds, view=FieldsView(embeds=self.embeds, embed=self.embed, items=self.items))

    @discord.ui.button(label='Imagem/Thumbnail', emoji=Emoji.splash, style=discord.ButtonStyle.gray, row=1)
    async def _image(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalImageAndThumbnail
        log.debug('Abrindo modal imagem/thumbnail embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalImageAndThumbnail(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Rodapé', emoji=Emoji.footer, style=discord.ButtonStyle.gray, row=1)
    async def _footer(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalFooter
        log.debug('Abrindo modal rodape embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalFooter(embeds=self.embeds, embed=self.embed))
    
    @discord.ui.button(label='Remover Embed', emoji=Emoji.delete, style=discord.ButtonStyle.red, row=1)
    async def _remove_embed(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .main_panel import MainView
        self.embeds.remove(self.embed)
        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
        log.info('Embed removida embed_builder user_id=%s', inter.user.id)
    
    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=2)
    async def _back(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .main_panel import MainView
        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
    
    @discord.ui.button(label='Enviar JSON', emoji=Emoji.exportar, style=discord.ButtonStyle.blurple, row=2)
    async def _send_json(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalSendJSON
        log.debug('Abrindo modal enviar JSON embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalSendJSON(embeds=self.embeds, embed=self.embed))

    @discord.ui.button(label='Obter JSON', emoji=Emoji.importar, style=discord.ButtonStyle.blurple, row=2)
    async def _get_json(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        embed_json = json.dumps(self.embed.to_dict(), ensure_ascii=True)
        await inter.response.send_message(f'```\n{embed_json}```', ephemeral=True)
        log.debug('JSON exibido embed_builder user_id=%s', inter.user.id)
