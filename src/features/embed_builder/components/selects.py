import discord
import logging

from src import NayulCore
from src.utils.emojis import Emoji
from src.utils.others import Colors
from ..edit_panel import EditEmbed
from ..utils import safe_emoji

log = logging.getLogger(__name__)

def _build_field_options(embed: discord.Embed) -> tuple[list[discord.SelectOption], bool]:
    if not embed.fields:
        return [discord.SelectOption(label='Nenhum campo encontrado')], True

    options = []
    for index, field in enumerate(embed.fields):
        label = field.name or 'Sem nome'
        label_display = label[:50] + '...' if len(label) >= 50 else label
        options.append(
            discord.SelectOption(
                label=f'{index + 1}. {label_display}',
                description=label_display,
                value=str(index),
            )
        )
    return options, False

class ChoiceEmbedSelect(discord.ui.Select):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item]) -> None:
        options = []
        for index, embed in enumerate(embeds):
            options.append(
                discord.SelectOption(
                    label=f'Embed {index + 1}',
                    description=embed.title[:50] + '...' if embed.title and len(embed.title) >= 50 else embed.title,
                    value=str(index),
                )
            )
        super().__init__(
            placeholder='Escolha uma embed para editar...',
            options=options,
            row=0
        )
        self.embeds=embeds
        self.items=items

    async def callback(self, inter: discord.Interaction[NayulCore]) -> None:
        embed = self.embeds[int(self.values[0])]
        await inter.response.edit_message(embed=embed, view=EditEmbed(embeds=self.embeds, embed=embed, items=self.items))
        log.debug('Embed selecionada index=%s user_id=%s', self.values[0], inter.user.id)

class ColorSelect(discord.ui.Select):
    def __init__(self, embeds: list[discord.Embed], embed: discord.Embed) -> None:
        self.embeds=embeds
        self.embed=embed
        options = [
            ('hex', 'Enviar código hexadecimal/decimal', Emoji.add),
            (discord.Color.red().value, 'Vermelho', None),
            (discord.Color.green().value, 'Verde', None),
            (discord.Color.blue().value, 'Azul', None),
            (discord.Color.purple().value, 'Roxo', None),
            (discord.Color.gold().value, 'Dourado', None),
            (discord.Color.orange().value, 'Laranja', None),
            (discord.Color.dark_red().value, 'Vermelho escuro', None),
            (discord.Color.dark_green().value, 'Verde escuro', None),
            (discord.Color.dark_blue().value, 'Azul escuro', None),
            (discord.Color.dark_purple().value, 'Roxo escuro', None),
            (discord.Color.dark_gold().value, 'Dourado escuro', None),
            (discord.Color.dark_orange().value, 'Laranja escuro', None),
            (discord.Color.blurple().value, 'Azul discord', None),
            (discord.Color.magenta().value, 'Magenta', None),
            (discord.Color.dark_magenta().value, 'Magenta escuro', None),
            (Colors.NIGHT_PURPLE, 'Roxo noturno', None),
            (Colors.VIBRANT_PURPLE, 'Roxo vibrante', None),
            (Colors.MYSTIC_PURPLE, 'Roxo mistico', None),
            (Colors.VIOLET_BLACK, 'Violeta escura', None),
            (Colors.ICY_WHITE, 'Branco gelado', None),
            ('random', 'Cor aleatória', None)
        ]

        super().__init__(
            placeholder='Editar a cor da embed...',
            options=[discord.SelectOption(label=label, emoji=emoji, value=str(value)) for value, label, emoji in options],
            row=1
        )

    async def callback(self, inter: discord.Interaction[NayulCore]) -> None:
        from .modals import ModalColor
        index = self.embeds.index(self.embed)

        match self.values[0]:
            case 'hex':
                await inter.response.send_modal(ModalColor(embeds=self.embeds, embed=self.embed))
            case 'random':
                self.embed.color = discord.Color.random()
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            case _:
                self.embed.color = int(self.values[0])
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
        log.debug('Cor selecionada embed_builder value=%s user_id=%s', self.values[0], inter.user.id)

class EditFieldSelect(discord.ui.Select):
    def __init__(self, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]) -> None:
        self.embeds=embeds
        self.embed=embed
        self.items=items
        options, disabled = _build_field_options(embed)

        super().__init__(
            placeholder='Escolha um campo para editar...',
            options=options,
            disabled=disabled,
        )
        
    async def callback(self, inter: discord.Interaction[NayulCore]) -> None:
        from .modals import ModalFields
        await inter.response.send_modal(ModalFields(embeds=self.embeds, embed=self.embed, items=self.items, index=int(self.values[0])))
        log.debug('Campo selecionado para editar index=%s user_id=%s', self.values[0], inter.user.id)

class DeleteFieldSelect(discord.ui.Select):
    def __init__(self, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]) -> None:
        self.embeds=embeds
        self.embed=embed
        self.items=items
        options, disabled = _build_field_options(embed)

        super().__init__(
            placeholder='Escolha um campo para deletar...',
            options=options,
            disabled=disabled,
        )

    async def callback(self, inter: discord.Interaction[NayulCore]) -> None:
        index = self.embeds.index(self.embed)

        try:
            self.embed.remove_field(int(self.values[0]))
            self.embeds[index] = self.embed

            from .views import FieldsView
            await inter.response.edit_message(embed=self.embed, view=FieldsView(embeds=self.embeds, embed=self.embed, items=self.items))
            log.info('Campo removido index=%s user_id=%s', self.values[0], inter.user.id)
        except discord.errors.HTTPException as e:
            if e.status == 400 and 'embeds.0.fields' in str(e):
                self.embed.description = 'A embed não pode ser vazia!'
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            else:
                await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)

class ChoiceItemSelect(discord.ui.Select):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item], item: discord.ui.Item | None) -> None:
        options = []
        if not items:
            options.append(
                discord.SelectOption(
                    label='Nenhum item encontrado',
                )
            )
            disabled = True
        else:
            disabled = False
            for index, item in enumerate(items):
                options.append(
                    discord.SelectOption(
                        emoji=safe_emoji(item.emoji),
                        label=item.label[:50] + '...' if item.label and len(item.label) >= 50 else item.label,
                        description=item.url[:50] + '...' if item.url and len(item.url) >= 50 else item.url,
                        value=str(index),
                    )
                )
        super().__init__(
            placeholder='Escolha um item para editar...',
            options=options,
            disabled=disabled,
            row=1
        )
        self.embeds = embeds
        self.items = items
        self.item = item

    async def callback(self, inter: discord.Interaction[NayulCore]) -> None:
        from .views import EditButtonView
        await inter.response.edit_message(view=EditButtonView(embeds=self.embeds, items=self.items, item=self.items[int(self.values[0])]))
        log.debug('Botao selecionado index=%s user_id=%s', self.values[0], inter.user.id)
