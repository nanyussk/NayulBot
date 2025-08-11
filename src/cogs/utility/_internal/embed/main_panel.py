import discord
import random

from src import NayulCore
from src.utils.emojis import Emoji
from src.utils.others import Colors

class MainView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        self.children[0].disabled= True if len(embeds) == 10 else False #Desabilita o botão caso atinja o limite de embeds.
        
        from .components.selects import ChoiceEmbedSelect
        self.add_item(ChoiceEmbedSelect(embeds=embeds, items=items))
        self.embeds=embeds
        self.items=items

    @discord.ui.button(label='Adicionar Embed', emoji=Emoji.add, style=discord.ButtonStyle.blurple, row=2)
    async def _add_embed(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
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
        await inter.response.edit_message(embeds=self.embeds, view=EditButtonView(embeds=self.embeds, items=self.items, item=None))

    @discord.ui.button(label='Enviar Embed', emoji=Emoji.send, style=discord.ButtonStyle.green, row=3)
    async def _send_embedd(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):

        view = discord.ui.View(timeout=None)
        for item in self.items:
            view.add_item(item)

        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
        await inter.channel.send(embeds=self.embeds, view=view)

    @discord.ui.button(label='Enviar em Webhook', emoji=Emoji.webhook, style=discord.ButtonStyle.green, row=3)
    async def _send_embed(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .components.modals import ModalWebhook
        await inter.response.send_modal(ModalWebhook(embeds=self.embeds, embed=self.embeds[0], items=self.items))