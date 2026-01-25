import re

import discord

def is_valid_url(url: str) -> bool:
    """Verifica se uma string fornecida é uma URL válida.

    Args:
        url (str): A string que será verificada.

    Returns:
        bool: Retorna True se a string for uma URL válida, caso contrário, False.
    """

    return bool(re.search(r'http[s]?://(?:[A-Za-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url))

def is_valid_color(hex_color: str | int) -> bool | ValueError:
    """Verifica se uma string ou inteiro fornecido é uma cor válida.

    A cor pode ser fornecida como uma string em formato hexadecimal (ex: '#ff0000')
    ou como um inteiro entre 0 e 16777215 (ex: 16711680).

    Args:
        hex_color (str | int): A string ou inteiro que será verificado.

    Returns:
        int: Retorna a cor em decimal.

    Raises:
        ValueError: Se a cor for inválida.
    """
    if isinstance(hex_color, int):
        if 0 <= hex_color <= 16777215:
            return hex_color
        raise ValueError('Cor inválida.')

    if not isinstance(hex_color, str):
        raise ValueError('Cor inválida.')

    value = hex_color.strip()
    if re.search(r'^#[a-fA-F0-9]+$', value):
        return int(value[1:], 16)
    if value.isdigit() and 0 <= int(value) <= 16777215:
        return int(value)
    raise ValueError('Cor inválida.')
    
def safe_emoji(emoji: str | discord.PartialEmoji) -> str | discord.PartialEmoji | None:
    """Verifica se um emoji é válido e seguro para ser exibido.

    Um emoji é considerado seguro se for uma instância de `discord.PartialEmoji` ou uma string que contenha um caractere Unicode de emoji entre U+2190 e U+1FAF6.

    Args:
        emoji (str | discord.PartialEmoji): O emoji que será verificado.

    Returns:
        str | discord.PartialEmoji | None: Retorna o emoji se ele for seguro, caso contrário, None.
    """
    if isinstance(emoji, discord.PartialEmoji):
        return emoji
    elif isinstance(emoji, str):
        if any("\u2190" <= ch <= "\U0001FAF6" for ch in emoji):
            return emoji
        return None
    return None
