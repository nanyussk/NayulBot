import discord
from discord.ext import commands

import asyncio
import logging

from src import NayulCore

log = logging.getLogger(__name__)

class OwnerCommands(commands.Cog):
    def __init__(self, nayul: NayulCore):
        self.nayul = nayul

    async def _reply(self, ctx: commands.Context[NayulCore], message: str, *, delete_after: int = 60) -> None:
        await ctx.reply(message, delete_after=delete_after, mention_author=False)

    def _is_extension(self, extension: str) -> bool:
        return extension in self.nayul.cog_manager.extensions

    @commands.command(name='sync', description='Sincroniza os comandos.')
    @commands.is_owner()
    async def sync(self, ctx: commands.Context[NayulCore]):
        """Sincroniza os comandos da Nayul com o Discord."""
        try:
            log.info('Sync comandos solicitado por user_id=%s', ctx.author.id)
            cmd = await self.nayul.tree.sync()
            await self._reply(ctx, f'Comandos sincronizados com sucesso. ({len(cmd)})')
        except Exception as exc:
            log.exception('Erro ao sincronizar comandos:', exc_info=exc)
            await self._reply(ctx, f'Erro ao sincronizar os comandos: {exc}')

    #-------------------- Staff Manager --------------------#

    @commands.group(name='staff')
    @commands.is_owner()
    async def staff(self, ctx: commands.Context[NayulCore]):
        """Gerencia os staffs da Nayul."""
        if not ctx.invoked_subcommand:
            await self._reply(ctx, 'Use um subcomando: add, remove ou list.')

    @staff.command(name='add', description='Adiciona um staff.')
    @commands.is_owner()
    async def add(self, ctx: commands.Context[NayulCore], user: discord.User):
        """Adiciona um staff à Nayul."""
        await self.nayul.db.settings.update_staffs('add', user.id)
        await self._reply(ctx, f'{user.mention} foi adicionado como staff.')
        log.info('Staff adicionado user_id=%s by=%s', user.id, ctx.author.id)

    @staff.command(name='remove', description='Remove um staff.')
    @commands.is_owner()
    async def remove(self, ctx: commands.Context[NayulCore], user: discord.User):
        """Remove um staff da Nayul."""
        await self.nayul.db.settings.update_staffs('remove', user.id)
        await self._reply(ctx, f'{user.mention} foi removido como staff.')
        log.info('Staff removido user_id=%s by=%s', user.id, ctx.author.id)
    
    @staff.command(name='list', description='Lista os staffs.')
    @commands.is_owner()
    async def list(self, ctx: commands.Context[NayulCore]):
        """Lista os staffs da Nayul."""
        settings = await self.nayul.db.settings.get_settings()
        ids = list(dict.fromkeys(settings.staffs + list(self.nayul.owner_ids)))
        # Busca usuarios em paralelo para reduzir tempo de resposta.
        results = await asyncio.gather(
            *[self.nayul.fetch_user(user_id) for user_id in ids],
            return_exceptions=True,
        )
        staffs = []
        for user_id, result in zip(ids, results):
            if isinstance(result, Exception):
                staffs.append(f'Desconhecido - {user_id}')
                continue
            staffs.append(f'{result.name} - {result.id}')
        await self._reply(ctx, '\n'.join(staffs) or 'Nenhum staff encontrado.', delete_after=120)
        log.debug('Lista de staffs enviada by=%s', ctx.author.id)

    #-------------------- Cog Manager --------------------#
        
    @commands.group(name='cog')
    @commands.is_owner()
    async def cogs(self, ctx: commands.Context[NayulCore]):
        """Gerencia as extensões da Nayul."""
        if not ctx.invoked_subcommand:
            await self._reply(ctx, 'Use um subcomando: reload, load, unload ou list.')

    @cogs.command(name='reload', description='Recarrega uma extensão.')
    @commands.is_owner()
    async def reload(self, ctx: commands.Context[NayulCore], extension: str):
        """Recarrega uma extensão ou todas as extensões da Nayul."""
        if extension == 'all':
            await self.nayul.cog_manager.reload_cogs(self.nayul)
            await self._reply(ctx, 'Todas as extensões foram recarregadas com sucesso.')
            log.info('Cogs recarregados (all) by=%s', ctx.author.id)
            return
        if not self._is_extension(extension):
            await self._reply(ctx, f'Extensão `{extension}` não encontrada. Use `{ctx.prefix}cog list` para verificar as extensões`', delete_after=10)
            return
        
        await self.nayul.cog_manager.reload_cog_one(self.nayul, extension)
        await self._reply(ctx, f'Extensão `{extension}` recarregada com sucesso.')
        log.info('Cog recarregado %s by=%s', extension, ctx.author.id)

    @cogs.command(name='load', description='Carrega uma extensão.')
    @commands.is_owner()
    async def load(self, ctx: commands.Context[NayulCore], extension: str):
        """Carrega uma extensão ou todas as extensões da Nayul."""
        if extension == 'all':
            await self.nayul.cog_manager.load_cogs(self.nayul)
            await self._reply(ctx, 'Todas as extensões foram carregadas com sucesso.')
            log.info('Cogs carregados (all) by=%s', ctx.author.id)
            return
        if not self._is_extension(extension):
            await self._reply(ctx, f'Extensão `{extension}` não encontrada. Use `{ctx.prefix}cog list` para verificar as extensões`', delete_after=10)
            return
        
        await self.nayul.cog_manager.load_cog_one(self.nayul, extension)
        await self._reply(ctx, f'Extensão `{extension}` carregada com sucesso.')
        log.info('Cog carregado %s by=%s', extension, ctx.author.id)

    @cogs.command(name='unload', description='Descarrega uma extensão.')
    @commands.is_owner()
    async def unload(self, ctx: commands.Context[NayulCore], extension: str):
        """Descarrega uma extensão ou todas as extensões da Nayul."""
        if extension == 'all':
            await self.nayul.cog_manager.unload_cogs(self.nayul)
            await self._reply(ctx, 'Todas as extensões foram descarregadas com sucesso.')
            log.info('Cogs descarregados (all) by=%s', ctx.author.id)
            return
        if not self._is_extension(extension):
            await self._reply(ctx, f'Extensão `{extension}` não encontrada. Use `{ctx.prefix}cog list` para verificar as extensões`', delete_after=10)
            return
        
        await self.nayul.cog_manager.unload_cog_one(self.nayul, extension)
        await self._reply(ctx, f'Extensão `{extension}` descarregada com sucesso.')
        log.info('Cog descarregado %s by=%s', extension, ctx.author.id)

    @cogs.command(name='list', description='Lista todas as extensões.')
    @commands.is_owner()
    async def extensions(self, ctx: commands.Context[NayulCore]):
        """Lista todas as extensões da Nayul."""
        extensions = sorted(self.nayul.cog_manager.extensions.keys())
        extensions_str = ' - all (Aplica em todas as extensões)\n - ' + '\n - '.join(extensions)
        await self._reply(ctx, f'Extensões:```\n{extensions_str}```', delete_after=120)
        log.debug('Lista de cogs enviada by=%s', ctx.author.id)

async def setup(nayul: NayulCore):
    await nayul.add_cog(OwnerCommands(nayul))
    log.debug('Cog OwnerCommands carregado.')
