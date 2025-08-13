import discord

from src import NayulCore
from src.utils.emojis import Emoji
from .selects import DeleteFieldSelect, EditFieldSelect

class FieldsView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]):
        super().__init__(timeout=None)
        self.children[1].disabled= True if len(embed.fields)==25 else False

        self.embeds=embeds
        self.embed=embed
        self.items=items

        self.add_item(EditFieldSelect(embeds=self.embeds, embed=self.embed, items=self.items))
        self.add_item(DeleteFieldSelect(embeds=self.embeds, embed=self.embed, items=self.items))

    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=3)
    async def close(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from ..edit_panel import EditEmbed
        await inter.response.edit_message(embeds=self.embeds, view=EditEmbed(embeds=self.embeds, embed=self.embed, items=self.items))

    @discord.ui.button(label='Adicionar Campo', emoji=Emoji.add, style=discord.ButtonStyle.blurple, row=3)
    async def delete(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .modals import ModalFields
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

    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=2)
    async def close(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from ..edit_panel import EditEmbed
        await inter.response.edit_message(embed=self.embed, view=EditEmbed(embeds=self.embeds, embed=self.embed, items=self.items))

class EditButtonView(discord.ui.View):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item], item: discord.ui.Item | None):
        super().__init__(timeout=None)
        self.embeds=embeds
        self.items=items
        self.item=item

        from .selects import ChoiceItemSelect
        self.add_item(ChoiceItemSelect(embeds=embeds, items=items, item=item))

        self.children[4].disabled = True if len(items) == 25 else False  # Desabilita o botão caso atinja o limite de botões.
        self.children[0].label = 'Nenhum item selecionado' if not item else "Item selecionado: " + (item.label[:10] + '...' if item.label and len(item.label) >= 10 else item.label) # Atualiza o label do botão com o nome do item selecionado.
        self.children[5].disabled = len(items) < 1  # Desabilita o botão de preview caso não haja botões.

        if not item:
            self.children[1].disabled = True
            self.children[2].disabled = True

    @discord.ui.button(label='.', disabled=True, style=discord.ButtonStyle.gray, row=0)
    async def _info_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        pass

    @discord.ui.button(label='Editar', emoji=Emoji.icon_edit, style=discord.ButtonStyle.blurple, row=0)
    async def edit_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .modals import ModalButton
        await inter.response.send_modal(ModalButton(embeds=self.embeds, items=self.items, item=self.item))

    @discord.ui.button(label='Remover', emoji=Emoji.delete, style=discord.ButtonStyle.red, row=0)
    async def remove_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        self.items.remove(self.item)

        from .views import EditButtonView
        await inter.response.edit_message(view=EditButtonView(embeds=self.embeds, items=self.items, item=None))

    @discord.ui.button(emoji=Emoji.back, style=discord.ButtonStyle.gray, row=2)
    async def _back(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from ..main_panel import MainView
        await inter.response.edit_message(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
    
    @discord.ui.button(label='Adicionar', emoji=Emoji.add, style=discord.ButtonStyle.green, row=2)
    async def _add_button(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        from .modals import ModalButton
        await inter.response.send_modal(ModalButton(embeds=self.embeds, items=self.items, item=None))
    
    @discord.ui.button(emoji='👀', style=discord.ButtonStyle.blurple, row=2)
    async def _preview(self, inter: discord.Interaction[NayulCore], button: discord.ui.Button):
        view = discord.ui.View(timeout=None)
        for item in self.items:
            view.add_item(item)

        await inter.response.send_message(content='**Visualização da embed com os botões:**', embeds=self.embeds, view=view, ephemeral=True)
