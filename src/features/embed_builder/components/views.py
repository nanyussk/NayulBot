import discord
import logging

from src import NayulCore
from src.utils.emojis import Emoji
from .selects import DeleteFieldSelect, EditFieldSelect

log = logging.getLogger(__name__)

class FieldsView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        # Field limit is 25 per embed.
        self.children[1].disabled = len(embed.fields) >= 25

        self.embeds=embeds
        self.embed=embed
        self.items=items

        self.add_item(EditFieldSelect(embeds=self.embeds, embed=self.embed, items=self.items))
        self.add_item(DeleteFieldSelect(embeds=self.embeds, embed=self.embed, items=self.items))
        log.debug('FieldsView iniciado fields=%s', len(embed.fields))

    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=3)
    async def close(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from ..edit_panel import EditEmbed
        log.debug('Fechando editor de campos user_id=%s', inter.user.id)
        await inter.response.edit_message(embeds=self.embeds, view=EditEmbed(embeds=self.embeds, embed=self.embed, items=self.items))

    @discord.ui.button(label='Adicionar Campo', emoji=Emoji.add, style=discord.ButtonStyle.blurple, row=3)
    async def delete(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .modals import ModalFields
        log.debug('Abrindo modal de campo embed_builder user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalFields(embeds=self.embeds, embed=self.embed, items=self.items))

class ColorView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        self.embeds=embeds
        self.embed=embed
        self.items=items

        from .selects import ColorSelect
        self.add_item(ColorSelect(embeds=self.embeds, embed=self.embed))
        self.add_item(
            discord.ui.Button(
                label='Encontrar cores',
                url='https://colorhunt.co/',
                style=discord.ButtonStyle.link,
                row=2
            )
        )
        log.debug('ColorView iniciado.')

    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=2)
    async def close(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from ..edit_panel import EditEmbed
        log.debug('Fechando ColorView user_id=%s', inter.user.id)
        await inter.response.edit_message(embed=self.embed, view=EditEmbed(embeds=self.embeds, embed=self.embed, items=self.items))

class EditButtonView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item], item: discord.ui.Item | None):
        super().__init__(timeout=None)
        self.embeds=embeds
        self.items=items
        self.item=item

        from .selects import ChoiceItemSelect
        self.add_item(ChoiceItemSelect(embeds=embeds, items=items, item=item))

        # Buttons are indexed based on decorator order; keep this block in sync.
        self.children[4].disabled = len(items) >= 25  # Limit of 25 buttons per view.
        self.children[0].label = self._format_item_label(item)
        self.children[5].disabled = len(items) < 1  # Disable preview when no buttons exist.

        if not item:
            self.children[1].disabled = True
            self.children[2].disabled = True
        log.debug('EditButtonView iniciado items=%s', len(items))

    def _format_item_label(self, item: discord.ui.Item | None) -> str:
        if not item or not getattr(item, 'label', None):
            return 'Nenhum item selecionado'
        label = item.label
        return f'Item selecionado: {label[:10]}{"..." if len(label) >= 10 else ""}'

    @discord.ui.button(label='.', disabled=True, style=discord.ButtonStyle.gray, row=0)
    async def _info_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        pass

    @discord.ui.button(label='Editar', emoji=Emoji.icon_edit, style=discord.ButtonStyle.blurple, row=0)
    async def edit_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .modals import ModalButton
        log.debug('Abrindo modal de botao user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalButton(embeds=self.embeds, items=self.items, item=self.item))

    @discord.ui.button(label='Remover', emoji=Emoji.delete, style=discord.ButtonStyle.red, row=0)
    async def remove_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        if not self.item:
            return

        self.items.remove(self.item)
        await inter.response.edit_message(view=EditButtonView(embeds=self.embeds, items=self.items, item=None))
        log.info('Botao removido embed_builder user_id=%s', inter.user.id)

    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=2)
    async def _back(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from ..main_panel import MainView
        log.debug('Retornando para MainView user_id=%s', inter.user.id)
        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
    
    @discord.ui.button(label='Adicionar', emoji=Emoji.add, style=discord.ButtonStyle.green, row=2)
    async def _add_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .modals import ModalButton
        log.debug('Abrindo modal adicionar botao user_id=%s', inter.user.id)
        await inter.response.send_modal(ModalButton(embeds=self.embeds, items=self.items, item=None))
    
    @discord.ui.button(emoji='👀', style=discord.ButtonStyle.blurple, row=2)
    async def _preview(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        view = discord.ui.View(timeout=None)
        for item in self.items:
            view.add_item(item)

        await inter.response.send_message(content='**Visualização da embed com os botões:**', embeds=self.embeds, view=view, ephemeral=True)
        log.debug('Preview de botoes embed_builder user_id=%s', inter.user.id)
