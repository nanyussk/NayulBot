import random
import logging

import discord

from src import NayulCore
from src.utils.emojis import Emoji
from src.utils.others import Colors

log = logging.getLogger(__name__)

class MainView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        # Limit of 10 embeds per message (Discord limit).
        self.children[0].disabled = len(embeds) >= 10
        
        from .components.selects import ChoiceEmbedSelect
        self.add_item(ChoiceEmbedSelect(embeds=embeds, items=items))
        self.embeds=embeds
        self.items=items
        log.debug('MainView embed_builder iniciada embeds=%s items=%s', len(embeds), len(items))

    def _build_items_view(self) -> discord.ui.View:
        view = discord.ui.View(timeout=None)
        for item in self.items:
            view.add_item(item)
        return view

    @discord.ui.button(label='Adicionar Embed', emoji=Emoji.add, style=discord.ButtonStyle.blurple, row=2)
    async def _add_embed(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        log.debug('Adicionando embed via painel user_id=%s', inter.user.id)
        self.embeds.append(
            discord.Embed(
                title=f'Título {len(self.embeds) + 1}',
                description='Descrição',
                color=random.choice(list(Colors.valid_colors()))
            )
        )
        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))

    @discord.ui.button(label='Editar Botões', emoji=Emoji.icon_link, style=discord.ButtonStyle.blurple, row=2)
    async def _edit_buttons(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.views import EditButtonView
        log.debug('Editando botoes embed_builder user_id=%s', inter.user.id)
        await inter.response.edit_message(embeds=self.embeds, view=EditButtonView(embeds=self.embeds, items=self.items, item=None))

    @discord.ui.button(label='Enviar Embed', emoji=Emoji.send, style=discord.ButtonStyle.green, row=3)
    async def _send_embedd(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        view = self._build_items_view()

        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
        if inter.channel:
            await inter.channel.send(embeds=self.embeds, view=view)
            log.info('Embeds enviadas em canal user_id=%s', inter.user.id)

    @discord.ui.button(label='Enviar em Webhook', emoji=Emoji.webhook, style=discord.ButtonStyle.green, row=3)
    async def _send_embed(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalWebhook
        log.debug('Abrindo modal webhook embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalWebhook(embeds=self.embeds, embed=self.embeds[0], items=self.items))
