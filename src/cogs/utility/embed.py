import json
import logging

import discord
from discord import app_commands
from discord.ext import commands

from src import NayulCore
from src.features import embed_builder
from src.utils.emojis import Emoji
from src.utils.others import Colors

log = logging.getLogger(__name__)

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
    async def _embed_create(self, inter: discord.Interaction[NayulCore]):
        log.info('Comando /embed criar user_id=%s', inter.user.id)
        embeds = [discord.Embed(title='Título 1', description='Descrição', color=Colors.NIGHT_PURPLE)]
        items: list[discord.ui.Item] = []
        await inter.response.send_message(
            embeds=embeds, view=embed_builder.MainView(embeds=embeds, items=items), ephemeral=True
        )

    async def _get_json(self, inter: discord.Interaction[NayulCore], message: discord.Message):
        if not message.embeds:
            return await inter.response.send_message(f'{Emoji.error} **|** A mensagem não possui embeds.', ephemeral=True)

        embeds = [
            discord.Embed(
                title=f'Embed {i}',
                description=f'```{json.dumps(embed.to_dict(), ensure_ascii=True)}```',
                color=Colors.NIGHT_PURPLE,
            )
            for i, embed in enumerate(message.embeds, start=1)
        ]
        await inter.response.send_message(embeds=embeds, ephemeral=True)
        log.debug('JSON de embeds enviado user_id=%s', inter.user.id)
    
    @app_commands.checks.has_permissions(manage_messages=True, embed_links=True)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def _copy_embed(self, inter: discord.Interaction[NayulCore], message: discord.Message):
        if not message.embeds:
            return await inter.response.send_message(f'{Emoji.error} **|** A mensagem não possui embeds.', ephemeral=True)

        if message.webhook_id and message.interaction:
            return await inter.response.send_message(f'{Emoji.error} **|** Não posso editar embeds de comandos.', ephemeral=True)
        
        embeds = list(message.embeds)
        items: list[discord.ui.Item] = []
        if message.components:
            # Copia apenas botoes para o painel de edicao.
            for item in discord.ui.View.from_message(message).children:
                if isinstance(item, discord.ui.Button):
                    items.append(item)

        await inter.response.send_message(embeds=embeds, view=embed_builder.MainView(embeds=embeds, items=items), ephemeral=True)
        log.info('Embed copiada para painel user_id=%s', inter.user.id)

async def setup(nayul: NayulCore):
    await nayul.add_cog(EmbedUtility(nayul))
    log.debug('Cog EmbedUtility carregado.')
