import json
import re
import logging

import aiohttp
import discord
import emoji as emoji_lib
from discord.ui import TextInput

from src import NayulCore
from src.utils.emojis import Emoji
from src.utils.others import Colors
from ..utils import is_valid_color, is_valid_url

log = logging.getLogger(__name__)

class ModalTitle(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Alterar título da embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._title = TextInput(
            label='Título da embed',
            placeholder='Defina o título da embed...',
            default=embed.title,
            style=discord.TextStyle.long,
            max_length=256,
            required=False
        )
        self._url = TextInput(
            label='URL do título',
            placeholder='URL que ficará no título...',
            style=discord.TextStyle.long,
            required=False
        )
        self.add_item(self._title)
        self.add_item(self._url)

    async def on_submit(self, inter: discord.Interaction[NayulCore]) -> None:
        index = self.embeds.index(self.embed) #Pega o index do embed atual

        try:
            if self._url.value and not is_valid_url(self._url.value):
                return await inter.response.send_message(f'{Emoji.error} **|** URL inválida.', ephemeral=True)
            
            self.embed.title = self._title.value
            self.embed.url = self._url.value
            self.embeds[index] = self.embed
            
            await inter.response.edit_message(embed=self.embed)
            log.debug('Titulo atualizado embed_builder user_id=%s', inter.user.id)
        except discord.errors.HTTPException as e:
            if e.status == 400 and 'embeds.0.description' in str(e):
                self.embed.description = 'A embed não pode ser vazia!'
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            else:
                await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)
                log.exception('Erro ao atualizar titulo embed_builder user_id=%s', inter.user.id)

class ModalDescription(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Alterar descrição da embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._description = TextInput(
            label='Descrição da embed',
            placeholder='Defina a descrição da embed...',
            default=embed.description,
            style=discord.TextStyle.paragraph,
            required=False
        )
        self.add_item(self._description)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual

        try:
            self.embed.description = self._description.value
            self.embeds[index] = self.embed
            
            await inter.response.edit_message(embed=self.embed)
            log.debug('Descricao atualizada embed_builder user_id=%s', inter.user.id)
        except discord.errors.HTTPException as e:
            if e.status == 400 and 'embeds.0.description' in str(e):
                self.embed.description = 'A embed não pode ser vazia!'
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            else:
                await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)
                log.exception('Erro ao atualizar descricao embed_builder user_id=%s', inter.user.id)

class ModalColor(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Alterar cor da embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._color = TextInput(
            label='Cor da embed (em hexadecimal ou decimal)',
            placeholder='Defina a cor da embed em hexadecimal ou decimal (ex: #ff0000 ou 16711680)',
            default=str(int(embed.color)) if embed.color else '',
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self._color)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual

        try:
            decimal_color = is_valid_color(self._color.value)

            self.embed.color = decimal_color
            self.embeds[index] = self.embed
            
            await inter.response.edit_message(embed=self.embed)
            log.debug('Cor atualizada embed_builder user_id=%s', inter.user.id)
        except ValueError:
            await inter.response.send_message(f'{Emoji.error} **|** Cor inválida! Defina a cor da embed em hexadecimal ou decimal. (ex: #ff0000 ou 16711680)', ephemeral=True)
            log.debug('Cor invalida embed_builder user_id=%s', inter.user.id)

class ModalAuthor(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Alterar autor da embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._author = TextInput(
            label='Nome do autor da embed',
            placeholder='Nome pequeno que ficara acima de tudo...',
            default=embed.author.name,
            max_length=256,
            style=discord.TextStyle.long,
            required=False
        )
        self._icon_url = TextInput(
            label='Imagem do autor',
            placeholder='Imagem que ficará ao lado do nome...',
            default=embed.author.icon_url,
            style=discord.TextStyle.long,
            required=False
        )
        self._url = TextInput(
            label='URL do autor',
            placeholder='Que ficará no nome do autor...',
            default=embed.author.url,
            style=discord.TextStyle.long,
            required=False
        )
        self.add_item(self._author)
        self.add_item(self._icon_url)
        self.add_item(self._url)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual
        try:
            if self._icon_url.value and not is_valid_url(self._icon_url.value):
                return await inter.response.send_message(f'{Emoji.error} **|** URL do autor inválida.', ephemeral=True)
            if self._url.value and not is_valid_url(self._url.value):
                return await inter.response.send_message(f'{Emoji.error} **|** URL inválida.', ephemeral=True)
            
            self.embed.set_author(name=self._author.value, icon_url=self._icon_url.value, url=self._url.value)
            self.embeds[index] = self.embed
            
            await inter.response.edit_message(embed=self.embed)
            log.debug('Autor atualizado embed_builder user_id=%s', inter.user.id)
        except discord.errors.HTTPException as e:
            if e.status == 400 and 'embeds.0.author' in str(e):
                self.embed.set_author(name=self._author.value, icon_url=self._icon_url.value, url=self._url.value)
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            else:
                await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)
                log.exception('Erro ao atualizar autor embed_builder user_id=%s', inter.user.id)

class ModalImageAndThumbnail(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Alterar imagem e thumbnail da embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._image = TextInput(
            label='Imagem da embed',
            placeholder='Insira uma url de imagem...',
            default=embed.image.url,
            style=discord.TextStyle.long,
            required=False
        )
        self._thumbnail = TextInput(
            label='Thumbnail da embed',
            placeholder='Insira uma url de imagem...',
            default=embed.thumbnail.url,
            style=discord.TextStyle.long,
            required=False
        )
        self.add_item(self._image)
        self.add_item(self._thumbnail)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual

        try:
            if self._image.value and not is_valid_url(self._image.value):
                return await inter.response.send_message(f'{Emoji.error} **|** URL da imagem inválida.', ephemeral=True)
            if self._thumbnail.value and not is_valid_url(self._thumbnail.value):
                return await inter.response.send_message(f'{Emoji.error} **|** URL da thumbnail inválida.', ephemeral=True)
            
            self.embed.set_image(url=self._image.value)
            self.embed.set_thumbnail(url=self._thumbnail.value)
            self.embeds[index] = self.embed
            
            await inter.response.edit_message(embed=self.embed)
            log.debug('Imagem/thumbnail atualizada embed_builder user_id=%s', inter.user.id)
        except discord.errors.HTTPException as e:
            if e.status == 400 and 'embeds.0.author' in str(e):
                self.embed.set_image(url=self._image.value)
                self.embed.set_thumbnail(url=self._thumbnail.value)
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            else:
                await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)
                log.exception('Erro ao atualizar imagem/thumbnail embed_builder user_id=%s', inter.user.id)

class ModalFields(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item], index: int | None = None):
        super().__init__(
            title='Editando campo da embed' if index is not None else 'Adicionando campo na embed', # Adapta o título para indicar se estamos editando um campo ou adicionando um novo campo.
            timeout=None)
        self.embeds=embeds
        self.embed=embed
        self.items=items
        self.index=index

        if index is not None:
            field = embed.fields[index]
            name, value, inline = field.name, field.value, field.inline
        else:
            name, value, inline = None, None, None

        self._name = TextInput(
            label='Nome do campo',
            placeholder='Insira o nome do campo...',
            default=name,
            max_length=256,
            style=discord.TextStyle.long,
            required=False
        )
        self._value = TextInput(
            label='Valor do campo',
            placeholder='Insira o valor do campo...',
            default=value,
            max_length=1024,
            style=discord.TextStyle.paragraph,
            required=False
        )
        self._inline = TextInput(
            label='Em linha?',
            default='sim' if inline else 'não',
            placeholder='sim/não | s/n | y/n | yes/no',
            style=discord.TextStyle.short,
            required=False
        )
        self.add_item(self._name)
        self.add_item(self._value)
        self.add_item(self._inline)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual
        mapping = {'sim': True, 's': True, 'y': True, 'yes': True, 'não': False, 'n': False, 'no': False}

        inline = mapping.get(self._inline.value.lower().casefold(), None) or False

        if self.index is not None:
            self.embed.set_field_at(self.index, name=self._name.value, value=self._value.value, inline=inline)
        else:
            self.embed.add_field(name=self._name.value, value=self._value.value, inline=inline)

        self.embeds[index] = self.embed

        from .views import FieldsView
        await inter.response.edit_message(embed=self.embed, view=FieldsView(embeds=self.embeds, embed=self.embed, items=self.items))
        log.debug('Campos atualizados embed_builder user_id=%s', inter.user.id)

class ModalFooter(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Alterar rodapé da embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._footer = TextInput(
            label='Texto do Rodapé',
            placeholder='Pequeno texto que ficara abaixo da embed...',
            default=embed.footer.text,
            style=discord.TextStyle.long,
            max_length=2048,
            required=False
        )
        self._url = TextInput(
            label='URL da rodapé',
            placeholder='Imagem que ficará ao lado do texto...',
            default=embed.footer.icon_url,
            style=discord.TextStyle.long,
            required=False
        )
        self.add_item(self._footer)
        self.add_item(self._url)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual

        try: 
            if self._url.value and not is_valid_url(self._url.value):
                return await inter.response.send_message(f'{Emoji.error} **|** URL do rodapé inválida.', ephemeral=True)
            
            self.embed.set_footer(text=self._footer.value, icon_url=self._url.value)
            self.embeds[index] = self.embed
            
            await inter.response.edit_message(embed=self.embed)
            log.debug('Rodape atualizado embed_builder user_id=%s', inter.user.id)
        except discord.errors.HTTPException as e:
            if e.status == 400 and 'embeds.0.footer' in str(e):
                self.embed.set_footer(text=self._footer.value, icon_url=self._url.value)
                self.embeds[index] = self.embed
                await inter.response.edit_message(embed=self.embed)
            else:
                await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)
                log.exception('Erro ao atualizar rodape embed_builder user_id=%s', inter.user.id)
            
class ModalSendJSON(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed):
        super().__init__(title='Envie o JSON de uma embed', timeout=None)
        self.embeds=embeds
        self.embed=embed

        self._json = TextInput(
            label='JSON',
            placeholder='Insira o JSON...',
            style=discord.TextStyle.paragraph,
            required=False
        )
        self.add_item(self._json)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        index = self.embeds.index(self.embed) #Pega o index do embed atual
        REGEX_CRASES = r'^`{3}|`{3}$'
        
        if re.search(REGEX_CRASES, self._json.value):
            json_str = re.sub(REGEX_CRASES, '', self._json.value)
        else:
            json_str = self._json.value

        try:
            json_data = json.loads(json_str)
            self.embed = discord.Embed.from_dict(json_data)
            self.embeds[index] = self.embed
            await inter.response.edit_message(embed=self.embed)
            log.debug('JSON aplicado embed_builder user_id=%s', inter.user.id)
        except json.JSONDecodeError:
            await inter.response.send_message(f'{Emoji.error} **|** Ocorreu um erro ao editar a embed.', ephemeral=True)
            log.debug('JSON invalido embed_builder user_id=%s', inter.user.id)

class ModalWebhook(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], embed: discord.Embed, items: list[discord.ui.Item]):
        super().__init__(title='Configure a Webhook', timeout=None)
        self.embeds=embeds
        self.embed=embed
        self.items=items

        self._name = TextInput(
            label='Nome da Webhook',
            placeholder='Insira o nome da Webhook...',
            max_length=30,
            style=discord.TextStyle.short,
            required=True
        )
        self._avatar = TextInput(
            label='Imagem da Webhook',
            placeholder='Insira o link da imagem...',
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self._name)
        self.add_item(self._avatar)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        if not is_valid_url(self._avatar.value):
            return await inter.response.send_message(f'{Emoji.error} **|** URL do avatar inválido.', ephemeral=True)
        
        if not inter.channel or not inter.guild:
            return await inter.response.send_message(f'{Emoji.error} **|** Não foi possível acessar o canal.', ephemeral=True)

        member = inter.guild.get_member(inter.client.user.id)
        if not member or not inter.channel.permissions_for(member).manage_webhooks:
            return await inter.response.send_message(f'{Emoji.error} **|** Eu preciso da permissão de `Gerenciar Webhooks` para enviar a embed.', ephemeral=True)

        embed_loading = discord.Embed(description=f'## {Emoji.loading_v1} **|** Enviando a embed...', color=Colors.MYSTIC_PURPLE)
        await inter.response.edit_message(embed=embed_loading, view=None)

        webhook_url: str | None = None
        for webhook in await inter.channel.webhooks():
            if webhook.token:
                webhook_url = webhook.url
                break

        if not webhook_url:
            new_webhook = await inter.channel.create_webhook(
                name=inter.client.user.name,
                reason=f'Para enviar a embed criada pela {inter.client.user.name} ({inter.client.user.id})')
            webhook_url = new_webhook.url

        view = discord.ui.View(timeout=None)
        for item in self.items:
            view.add_item(item)

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            await webhook.send(embeds=self.embeds, view=view, username=self._name.value, avatar_url=self._avatar.value)

            from ..main_panel import MainView
            await inter.edit_original_response(embeds=self.embeds, view=MainView(embeds=self.embeds, items=self.items))
            log.info('Embeds enviadas via webhook user_id=%s', inter.user.id)

class ModalButton(discord.ui.Modal):
    def __init__(self, *, embeds: list[discord.Embed], items: list[discord.ui.Item], item: discord.ui.Item):
        super().__init__(
            title='Editando Botão' if item else 'Adicionando Botão', timeout=None
        )
        self.embeds=embeds
        self.items=items
        self.item=item
        
        if item:
            label, url, emoji = item.label, item.url, item.emoji
        else:
            label, url, emoji = None, None, None
        emoji_default = str(emoji) if emoji else None

        self._name = TextInput(
            label='Nome do Botão',
            placeholder='Insira o nome do botão...',
            default=label,
            style=discord.TextStyle.short,
            required=True
        )
        self._url = TextInput(
            label='URL do Botão',
            placeholder='Insira o link do botão...',
            default=url,
            style=discord.TextStyle.short,
            required=True
        )
        self._emoji = TextInput(
            label='Emoji do Botão (Opcional)',
            placeholder='Insira o emoji do botão...',
            default=emoji_default,
            style=discord.TextStyle.short,
            required=False
        )
        self.add_item(self._name)
        self.add_item(self._url)
        self.add_item(self._emoji)

    async def on_submit(self, inter: discord.Interaction[NayulCore]):
        if not is_valid_url(self._url.value):
            return await inter.response.send_message(f'{Emoji.error} **|** URL do botão inválido.', ephemeral=True)
        
        emoji_value = None
        if self._emoji.value:
            if (custom_emoji := discord.PartialEmoji.from_str(self._emoji.value)):
                emoji_value = custom_emoji
            elif emoji_lib.is_emoji(self._emoji.value):
                emoji_value = self._emoji.value
            else:
                return await inter.response.send_message(f'{Emoji.error} **|** Emoji do botão inválido ou não encontrado.', ephemeral=True)
            
        if self.item:
            self.items[self.items.index(self.item)] = discord.ui.Button(
                label=self._name.value,
                url=self._url.value,
                emoji=emoji_value
            )
        else:
            self.items.append(
                discord.ui.Button(
                    label=self._name.value,
                    url=self._url.value,
                    emoji=emoji_value
                )
            )

        from .views import EditButtonView
        await inter.response.edit_message(view=EditButtonView(embeds=self.embeds, items=self.items, item=self.item))
        log.debug('Botao atualizado embed_builder user_id=%s', inter.user.id)
