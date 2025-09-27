import os
import yaml
from datetime import datetime
from typing import Union, Literal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Colors:
    MYSTIC_PURPLE   = 4927093
    VIBRANT_PURPLE  = 10834034
    VIOLET_BLACK    = 2831035
    ICY_WHITE       = 15921906
    NIGHT_PURPLE    = 1708071

    @classmethod
    def valid_colors(cls) -> list[int]:
        return [
            cls.MYSTIC_PURPLE,
            cls.VIBRANT_PURPLE,
            cls.VIOLET_BLACK,
            cls.NIGHT_PURPLE
        ]

def format_timestamp(date: Union[datetime, int, str], style: Literal['t','T','f','F','d','D','R']) -> str:
	"""Formata o timestamp.
	Args:
		date (`Union[datetime, int, str]`): Data a ser formatada.
			- `datetime`: Objeto datetime.
			- `int`: Timestamp em segundos.
			- `str`: Data no formato ISO: "YYYY-MM-DD HH:MM[:SS]".
		style (`Literal['t','T','f','F','d','D','R']`): Estilo de formatação.
			- `t`: Hora curta (ex: 12:34).
			- `T`: Hora longa (ex: 12:34:56).
			- `f`: Data e hora curta (ex: 12 de janeiro de 2023 às 12:34).
			- `F`: Data e hora longa (ex: quarta-feira, 12 de janeiro de 2023 às 12:34).
			- `d`: Data curta (ex: 12/01/2023).
			- `D`: Data longa (ex: quarta-feira, 12/01/2023).
			- `R`: Relativo (ex: há 5 minutos).
	Returns:
		str: Timestamp formatado.
	Raises:
		ValueError: Se o valor `date` não for válido.
	"""
	if isinstance(date, datetime):
		timestamp = date.timestamp()
	elif isinstance(date, int):
		timestamp = date
	elif isinstance(date, str):
		try:
			date_dt = datetime.fromisoformat(date)
			timestamp = int(date_dt)
		except ValueError:
			raise ValueError(f'A data fornecida "{date}" não é uma data válida no formato ISO: "YYYY-MM-DD HH:MM[:SS]".')
	else:
		raise ValueError(f'O tipo de dado fornecido "{type(date)}" não é suportado. Use datetime, int ou str no formato ISO.')

	return f'<t:{int(timestamp)}:{style}>'
		

def Permissions() -> dict:
	"""Carrega as permissões em Português do arquivo permissions.yml."""
	with open(BASE_DIR + '/resources/permissions.yml', 'r', encoding='utf-8') as file:
		return yaml.safe_load(file) or {}

def read_txt_file(path: str) -> str | None:
    with open(f'{BASE_DIR}/{path}', 'r', encoding='utf-8') as file:
        return file.read() or None
