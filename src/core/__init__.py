import discord
from discord.ext import commands

import os
import logging
import asyncio
import aiohttp
from time import time

from src.config import ENV, setup_runtime_env
from .emoji_manager import EmojiManager
from .cog_manager import CogManager
from .restrict_help import RestrictedHelpCommand
from src.database import DatabaseClient

log = logging.getLogger(__name__)

class NayulCore(commands.AutoShardedBot):
    """
    Esta classe é responsável por inicializar o bot, carregar as extensões e gerenciar os eventos.
    """
    def __init__(self):
        setup_runtime_env()
        intents = discord.Intents.all()
        intents.message_content = True  # Necessário para ler o conteúdo das mensagens
        intents.members = True # Necessário para acessar informações dos membros
        super().__init__(
            command_prefix=commands.when_mentioned_or(ENV.PREFIX),
            intents=intents,
            help_command=RestrictedHelpCommand(),
        )
        #------- atributos do bot -------#
        self.owner_ids = set()
        self.uptime = time()

        #------- classes de configuração do bot -------#
        self.db: DatabaseClient = None
        self.session = aiohttp.ClientSession()
        self.cog_manager = CogManager()
        self.emoji_manager = EmojiManager()

        #Adicionando os IDs dos proprietários definidos no .env.
        for owner_id in ENV.OWNER_IDS:
            try:
                self.owner_ids.add(owner_id)
            except ValueError:
                log.warning(f'ID de proprietário inválido: {owner_id}')
                    
    async def setup_hook(self):
            """Método chamado enquanto o bot está inicinado."""
            log.debug('setup_hook iniciado.')
            try:
                self.db = await DatabaseClient.connect()
            except Exception:
                log.critical('Falha ao conectar no banco, encerrando.')
                await self.close()
                return

            await self.emoji_manager.config_emojis(self)
            await self.cog_manager.load_cogs(self)
            await self.load_extension('jishaku')
            log.debug('setup_hook finalizado.')

    async def on_ready(self):
            """Método chamado quando o bot está pronto."""
            log.info(f'Conectado como {self.user} ({self.user.id}).')
            log.info(f'Latência: {round(self.latency * 1000)}ms.')
            log.info(f'discord.py: {discord.__version__}.')
            log.info(f'Python: {os.sys.version.split()[0]}.')
            log.info(f'Servidores: {len(self.guilds)}.')
            log.info("Proprietários: " + ", ".join(f"{u.name} ({u.id})" if u else f"Desconhecido ({oid})" for u, oid in zip(await asyncio.gather(*[self.fetch_user(oid) for oid in self.owner_ids], return_exceptions=True), self.owner_ids)))

    async def start(self, token, *, reconnect = True):
        """Método chamado para iniciar o bot."""
        log.info('Iniciando cliente Discord...')
        return await super().start(token, reconnect=reconnect)
    
    async def close(self):
        """Método chamado quando o bot é fechado."""
        log.info('Desconectando...')
        await self.session.close()
        await super().close()
        log.info('🔴 Bot desconectado.')
