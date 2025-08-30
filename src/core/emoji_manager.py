import os
import re
import asyncio
import logging
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from src import NayulCore

from src.env import ENV
from src.utils.emojis import Emoji


log = logging.getLogger(__name__)

class EmojiManager:
    """Classe responsável por gerenciar os emojis do bot."""
    def __init__(self):
        pass

    async def config_emojis(self, nayul: 'NayulCore'):
        """Carrega e configura os emojis do bot.
        Args:
            nayul (`NayulCore`): Instância do bot.
        """

        log.warning('Iniciando configuração dos emojis...')
        existing_emojis = {emoji.name: emoji for emoji in await nayul.fetch_application_emojis()}  # Obtém os emojis existentes na aplicação
        formats = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
        emojis_data = {}

        async with nayul.session.get(f'{ENV.INTERNAL_API}/emojis') as response:
            if response.status != 200:
                log.critical(f'Erro ao acessar a URL: {response.status}') 
                return

            files = await response.json() # Obtém a lista de arquivos do repositório
            semaphore = asyncio.Semaphore(5)  # Limita o número de downloads simultâneos

            async def process_emoji(file: dict):
                name, ext = os.path.splitext(file['filename'])
                if ext.lower() not in formats:
                    log.warning(f'Formato inválido: {file["filename"]}')
                    return
                
                emoji_name = name.lower()
                if emoji_name in existing_emojis: # Verifica se o emoji já existe
                    emoji = existing_emojis[emoji_name]
                    emoji_mention = f'<a:{emoji.name}:{emoji.id}>' if emoji.animated else f'<:{emoji.name}:{emoji.id}>'
                    emojis_data[emoji_name] = emoji_mention
                    return
                
                async with semaphore:
                    try:
                        async with nayul.session.get(file['url']) as img_response:
                            if img_response.status != 200:
                                log.critical(f'Erro ao baixar o emoji: {img_response.status}')
                                return
                            
                            image_bytes = await img_response.read()
                            emoji_created = await nayul.create_application_emoji(
                                name=emoji_name,
                                image=image_bytes
                            ) # Cria o emoji
                            emoji_mention = f'<a:{emoji_created.name}:{emoji_created.id}>' if emoji_created.animated else f'<:{emoji_created.name}:{emoji_created.id}>'
                            emojis_data[emoji_name] = emoji_mention
                            log.info(f'✨ Emoji {emoji_name} criado com sucesso.')
                    except Exception:
                        log.error(f'Erro ao criar emoji {emoji_name}', exc_info=True)
            
        await asyncio.gather(*(process_emoji(file) for file in files))
        await self.generate_emoji_class(emojis_data)

    async def generate_emoji_class(self, emojis: Dict[str, str]):
        """Gera uma classe ou atualiza a classe de emojis automaticamente.
        Args:
            emojis (`Dict[str, str]`): Dicionário de emojis.
        """

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, 'utils', 'emojis.py')
            
        class_lines = [
            'class Emoji:\n',
            '    """Classe para armazenar os emojis do bot."""\n'
        ]
        for key, value in emojis.items():
            class_lines.append(f'    {key} = {value!r}\n')

        class_lines += [
            '\n',
            '    @classmethod\n',
            '    def update(cls, **kwargs):\n',
            '        """Atualiza os emojis dinamicamente."""\n',
            '        for key, value in kwargs.items():\n',
            '            setattr(cls, key, value)\n'
            '\n',
            '    @classmethod\n',
            '    def as_dict(cls) -> dict:\n',
            '        """Retorna os emojis como um dicionário."""\n',
            '        return {k: v for k, v in cls.__dict__.items() if not k.startswith("__")}\n'
        ]
        new_class = ''.join(class_lines)

        with open(output_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()

        updated_content = re.sub(
            r'class Emoji:.*?(?=^@|\Z)',
            new_class,
            existing_content,
            flags=re.DOTALL | re.MULTILINE
        ) # Substitui a classe existente ou adiciona a nova

        if updated_content != existing_content:
            log.warning('Atualizando a classe Emoji...')
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                Emoji.update(**emojis)
            
        log.info('✅ Emojis configurados com sucesso.')