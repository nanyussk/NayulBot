import discord
from discord import app_commands
from discord.ext import commands

import json

from src import NayulCore
from src.utils.others import Colors
from src.utils.emojis import Emoji

from ._internal import embed


class EmbedUtility(commands.Cog):
    def __init__(self, nayul: NayulCore) -> None:
        self.nayul: NayulCore = nayul
        self.nayul.tree.add_command(
            app_commands.ContextMenu(
                name='Obter JSON',
                callback=self._get_json
            )
        )
        self.nayul.tree.add_command(
            app_commands.ContextMenu(
                name='Copiar Embed',
                callback=self._copy_embed
            )
        )

    embed: app_commands.Group = app_commands.Group(
        name='embed', description='Comando de criação de embeds e components'
    )

    @embed.command(name='criar', description='Abra um painel de criação de embeds')
    @app_commands.checks.has_permissions(manage_messages=True, embed_links=True)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    @app_commands.choices(
        embed_type=[
            app_commands.Choice(name='Embed', value=1),
            app_commands.Choice(name='Components V2', value=2),
        ]
    )
    async def _embed_create(self, inter: discord.Interaction, embed_type: app_commands.Choice[int]):
        if embed_type.value == 1:
            embeds: list[discord.Embed] = []
            items: list[discord.ui.Item] = []

            embeds.append(discord.Embed(title='Título 1', description='Descrição', color=Colors.NIGHT_PURPLE))
            await inter.response.send_message(
                embeds=embeds, view=embed.MainView(embeds=embeds, items=items), ephemeral=True
            )
        else:
            await inter.response.send_message('Em breve...', ephemeral=True)

    async def _get_json(self, inter: discord.Interaction, message: discord.Message):
        if not message.embeds:
            return await inter.response.send_message(f'{Emoji.error} **|** A mensagem não possui embeds.', ephemeral=True)
        embeds = []
        for i, embed in enumerate(message.embeds, start=1):
           embeds.append(discord.Embed(title=f'Embed {i}', description=f'```{json.dumps(embed.to_dict(), ensure_ascii=True)}```', color=Colors.NIGHT_PURPLE))
        await inter.response.send_message(embeds=embeds, ephemeral=True)
    
    @app_commands.checks.has_permissions(manage_messages=True, embed_links=True)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def _copy_embed(self, inter: discord.Interaction, message: discord.Message):
        if not message.embeds:
            return await inter.response.send_message(f'{Emoji.error} **|** A mensagem não possui embeds.', ephemeral=True)

        elif message.webhook_id and message.interaction:
            return await inter.response.send_message(f'{Emoji.error} **|** Não posso editar embeds de comandos.', ephemeral=True)
        
        embeds = []
        for _embed in message.embeds:
            embeds.append(_embed)
        
        items = []
        for item in discord.ui.View.from_message(message).children:
            if isinstance(item, discord.ui.Button):
                items.append(item)

        await inter.response.send_message(embeds=embeds, view=embed.MainView(embeds=embeds, items=items), ephemeral=True)

async def setup(nayul: NayulCore):
    await nayul.add_cog(EmbedUtility(nayul))