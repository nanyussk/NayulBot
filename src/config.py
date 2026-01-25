import os
import logging

from dotenv import load_dotenv

load_dotenv()

from .env import ENV

log = logging.getLogger(__name__)

def setup_runtime_env() -> None:
    log.debug('Configurando variaveis de ambiente de runtime.')
    os.environ.update(
        {
            'JISHAKU_NO_UNDERSCORE': 'True',  # Desativa o prefixo de sublinhado para os comandos do Jishaku
            'JISHAKU_NO_DM_TRACEBACK': 'True',  # Desativa o envio de mensagens de erro por DM
            'JISHAKU_HIDE': 'True',  # Esconde os comandos do Jishaku na lista de comandos disponíveis
            'JISHAKU_FORCE_PAGINATOR': 'True',  # Força o uso do paginador do Jishaku
        }
    )
    log.debug('Variaveis de runtime configuradas.')


__all__ = ['ENV', 'setup_runtime_env']
