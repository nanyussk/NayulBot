import os
import logging
from typing import Dict

log = logging.getLogger(__name__)

def discover_cog_modules(path: str = 'src/cogs') -> Dict[str, str]:
    modules: Dict[str, str] = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isabs(path):
        path = os.path.join(base_dir, os.path.normpath(path).lstrip(os.path.sep))
    log.debug('Descobrindo cogs em: %s', path)
    for root, _, files in os.walk(path):
        if '_internal' in root.split(os.path.sep):
            continue
        for file in sorted(files):
            if not file.endswith('.py') or file.startswith('_'):
                continue
            rel_path = os.path.relpath(os.path.join(root, file), start=base_dir)
            if rel_path.startswith('cogs' + os.path.sep):
                rel_path = 'src' + os.path.sep + rel_path
            module = rel_path[:-3].replace(os.path.sep, '.')
            modules[module] = module
            log.debug('Cog encontrado: %s', module)
    log.info('Total de cogs encontrados: %s', len(modules))
    return modules


__all__ = ['discover_cog_modules']
