import logging
from typing import TYPE_CHECKING, Dict

from .cog_registry import discover_cog_modules

if TYPE_CHECKING:
    from src import NayulCore

log = logging.getLogger(__name__)

class CogManager:
    """ Classe responsável por gerenciar as extensões (cogs) do bot. """
    def __init__(self, path: str = 'src/cogs'):
        self.path = path
        self.extensions: Dict[str, str] = {} # Armazena as extensões como um dicionário

    def _refresh_extensions(self) -> None:
        log.debug('Atualizando lista de extensoes.')
        self.extensions = discover_cog_modules(self.path)
        log.debug('Extensoes carregadas: %s', len(self.extensions))

    def _resolve_extension(self, extension: str) -> str:
        if extension in self.extensions:
            return self.extensions[extension]
        matches = [module for module in self.extensions.values() if module.endswith(f'.{extension}')]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            log.error('Extensao nao encontrada: %s', extension)
            raise KeyError(f'Extensao nao encontrada: {extension}')
        log.error('Extensao ambigua: %s', extension)
        raise KeyError(f'Extensao ambigua: {extension}')

    async def load_cogs(self, nayul: 'NayulCore'):
        """ Carrega todas as extensões do bot. """
        self._refresh_extensions()
        for key, module in self.extensions.items():
            try:
                await nayul.load_extension(module)
                log.info(f'✅ Carregado {key!r}.')
            except Exception:
                log.exception(f'Erro ao carregar a extensão {key!r}:')
                continue

    async def reload_cogs(self, nayul: 'NayulCore'):
        """ Recarrega todas as extensões do bot. """
        self._refresh_extensions()
        for key, module in self.extensions.items():
            try:
                await nayul.reload_extension(module)
                log.debug(f'🔄 Recarregado {key!r}.')
            except Exception:
                log.exception(f'Erro ao recarregar a extensão {key!r}:')
                continue

    async def unload_cogs(self, nayul: 'NayulCore'):
        """ Descarrega as extensões do bot. """
        for key, module in self.extensions.items():
            try:
                await nayul.unload_extension(module)
                log.debug(f'❌ Descarregado {key!r}')
            except Exception:
                log.exception(f'Erro ao descarregar a extensão {key!r}:')
                continue
    
    async def reload_cog_one(self, nayul: 'NayulCore', extension: str):
        """ Recarrega uma extensão do bot. """
        try:
            module = self._resolve_extension(extension)
            await nayul.reload_extension(module)
            log.debug(f'🔄 Recarregado {extension!r}.')
        except Exception:
            log.exception(f'Erro ao recarregar a extensão {extension!r}:')

    async def load_cog_one(self, nayul: 'NayulCore', extension: str):
        """ Carrega uma extensão do bot. """
        try:
            if not self.extensions:
                self._refresh_extensions()
            module = self._resolve_extension(extension)
            await nayul.load_extension(module)
            log.debug(f'✅ Carregado {extension!r}.')
        except Exception:
            log.exception(f'Erro ao carregar a extensão {extension!r}:')
    
    async def unload_cog_one(self, nayul: 'NayulCore', extension: str):
        """ Descarrega uma extensão do bot. """
        try:
            module = self._resolve_extension(extension)
            await nayul.unload_extension(module)
            log.debug(f'❌ Descarregado {extension!r}.')
        except Exception:
            log.exception(f'Erro ao descarregar a extensão {extension}:')
