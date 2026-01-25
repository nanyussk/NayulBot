import os
import sys
import logging
from typing import List
from dataclasses import dataclass

log = logging.getLogger(__name__)

def _str_to_list_of_ints(value: str) -> List[int]:
    return [int(v.strip()) for v in value.split(',') if v.strip().isdigit()]

def _validate_required(var_name: str, validator=lambda x: bool(x)) -> str:
    value = os.getenv(var_name)
    if not value or not validator(value):
        log.critical(f'[ENV] Erro: a variável obrigatória "{var_name}" está ausente ou inválida.')
        sys.exit(1)
    return value


@dataclass
class Env:
    '''
    Classe para armazenar as variáveis de ambiente do bot.
    '''
    # Obrigatórios
    TOKEN: str
    OWNER_IDS: List[int]
    MONGO: str
    FILES_API: str

    # Opcionais (com valores padrão)
    PREFIX: str = ',,'

    @classmethod
    def load(cls) -> 'Env':
        log.debug('Carregando variaveis de ambiente.')
        return cls(
            TOKEN=_validate_required('TOKEN'),
            OWNER_IDS=_str_to_list_of_ints(_validate_required('OWNER_IDS')),
            FILES_API=_validate_required('FILES_API'),
            PREFIX=os.getenv('PREFIX', ',,'),
            MONGO=_validate_required('MONGO')
        )

ENV = Env.load()
