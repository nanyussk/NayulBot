import os
import sys
import logging
from dotenv import load_dotenv
from typing import List, Optional
from dataclasses import dataclass

load_dotenv()

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
    INTERNAL_API: str

    # Opcionais (com valores padrão)
    PREFIX: str = ',,'
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_USERNAME: Optional[str] = None

    @classmethod
    def load(cls) -> 'Env':
        return cls(
            TOKEN=_validate_required('TOKEN'),
            GITHUB_TOKEN=os.getenv('GITHUB_TOKEN', None),
            GITHUB_USERNAME=os.getenv('GITHUB_USERNAME', None),
            OWNER_IDS=_str_to_list_of_ints(_validate_required('OWNER_IDS')),
            INTERNAL_API=_validate_required('INTERNAL_API'),
            PREFIX=os.getenv('PREFIX', ',,'),
            MONGO=_validate_required('MONGO')
        )

ENV = Env.load()