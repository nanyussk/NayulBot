import os
import re
import discord
import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core import NayulCore

from src.config import ENV
from src.utils.emojis import Emoji

log = logging.getLogger(__name__)

def _format_emoji(emoji: discord.Emoji):
    return f'<a:{emoji.name}:{emoji.id}>' if emoji.animated else f'<:{emoji.name}:{emoji.id}>'

class EmojiManager:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5) # Limita quantos emojis podem ser criados simultaneamente
        self.base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Raiz do projeto
        self.emojis_path: str = 'files/emojis/default'
        self.formats: tuple[str] = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
        self.existing_emojis: dict[str, str] = {}
        self.emojis_data: dict[str, str] = {}
        self.error_occurred: int = 0

    async def __generate_emoji_class(self, emojis: dict[str, str]):
        """
        Gera/atualiza a classe Emoji em emojis.py com os emojis atuais.
        """
        output_path = os.path.join(self.base_dir, 'utils', 'emojis.py')
        
        class_lines = [
            'class Emoji:\n',
        ]
        for key, value in emojis.items():
            class_lines.append(f'\t{key} = {value!r}\n') # Cria atributo dinâmico para cada emoji

        class_lines += [
            '\n',
            '\t@classmethod\n',
            '\tdef update(cls, **kwargs):\n',
            '\t\tfor key, value in kwargs.items():\n',
            '\t\t\tsetattr(cls, key, value)\n'
            '\n',
            '\t@classmethod\n',
            '\tdef as_dict(cls) -> dict:\n',
            '\t\t\treturn {k: v for k, v in cls.__dict__.items() if not k.startswith("__")}\n'
        ]
        new_class = ''.join(class_lines)

        with open(output_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()

        updated_content = re.sub(
            r'class Emoji:.*?(?=^@|\Z)', # Substitui a classe inteira no arquivo
            new_class,
            existing_content,
            flags=re.DOTALL | re.MULTILINE
        )

        if updated_content != existing_content:
            log.info('Atualizando emojis.py...')
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                Emoji.update(**emojis) # Atualiza a classe em memória
        
        log.info('Emojis.py configurado com sucesso.')

    async def __process_emoji(self, file: dict, nayul: 'NayulCore'):
        """
        Cria um emoji a partir de uma URL da API se ele ainda não existir.
        """
        name, ext = os.path.splitext(file['filename'])

        if ext.lower() not in self.formats:
            log.warning(f'Emoji {file["filename"]} não é suportado. Ignorando...')
            return
        
        emoji_name = name.lower()
        if emoji_name in self.existing_emojis:
            emoji = self.existing_emojis[emoji_name]
            emoji_mention = _format_emoji(emoji)
            self.emojis_data[emoji_name] = emoji_mention
            return
        
        async with self.semaphore:
            try:
                async with nayul.session.get(file['url']) as emoji_resp:
                    if emoji_resp.status != 200:
                        log.error(f'Erro ao buscar emoji {file["filename"]}: {emoji_resp.status}')
                        return
                
                    emoji_bytes = await emoji_resp.read()
                    emoji = await nayul.create_application_emoji(
                        name=emoji_name,
                        image=emoji_bytes
                    )
                    emoji_mention = _format_emoji(emoji)
                    self.emojis_data[emoji_name] = emoji_mention
                    log.info(f'✨ Emoji {emoji_name} adicionado com sucesso.')
                    
            except Exception:
                log.exception(f'Erro ao processar emoji {file["filename"]}:')

    async def __process_local_emoji(self, nayul: 'NayulCore', emojis_path: str, image: str):
        """
        Cria emojis a partir de arquivos locais.
        """
        name, ext = os.path.splitext(image)
        emoji_name, emoji_ext = name.lower(), ext.lower()

        if emoji_ext not in self.formats:
            log.warning(f'Emoji {image} não é suportado. Ignorando...')
            return
        
        if emoji_name in self.existing_emojis:
            emoji = self.existing_emojis[emoji_name]
            emoji_mention = _format_emoji(emoji)
            self.emojis_data[emoji.name] = emoji_mention
            return
        
        async with self.semaphore:
            path = os.path.join(emojis_path, image)
            with open(path, 'rb') as file:
                emoji_created = await nayul.create_application_emoji(name=emoji_name, image=file.read())
                self.emojis_data[emoji_created.name] = _format_emoji(emoji_created)
                log.info(f'✨ Emoji {emoji_name} adicionado com sucesso.')

    async def _get_emojis(self, nayul: 'NayulCore'):
        """
        Busca emojis da API, GitHub RAW ou localmente, processando todos em paralelo.
        """

        if self.existing_emojis == Emoji.as_dict(): # Já carregados, nada a fazer
            self.emojis_data = self.existing_emojis
            return

        if ENV.FILES_API:
            try:
                async with nayul.session.get(f'{ENV.FILES_API}/{self.emojis_path}') as resp:
                    if resp.status != 200:
                        raise Exception(f'API retornou {resp.status}')
            
                    files = await resp.json()

                    await asyncio.gather(*[self.__process_emoji(file, nayul) for file in files])
                    return
            
            except Exception as e:
                log.warning(f'⚠️ Falha ao buscar emojis da API: {e}. Tentando GitHub RAW/API...')
                try:
                    async with nayul.session.get(f'https://api.github.com/repos/nanyussk/Files-Bank/contents/{self.emojis_path}') as resp:
                        if resp.status != 200:
                            raise Exception(f'API do GitHub retornou {resp.status}')
                        
                    files = [{f['name']: f['download_url'] for f in await resp.json()}]

                    await asyncio.gather(*[self.__process_emoji(file, nayul) for file in files])
                    return

                except Exception as e:
                    log.critical(f'⚠️ Falha ao buscar emojis no GitHub RAW/API: {e}')
                    await nayul.close()
        else:
            emojis_path = f'{self.base_dir}/resources/emojis'
            if not os.path.exists(emojis_path):
                raise Exception(f'Nenhum emoji local encontrado em {emojis_path}')
                
            await asyncio.gather(*[
                self.__process_local_emoji(nayul, emojis_path, image)
                for image in os.listdir(emojis_path)
                if os.path.isfile(os.path.join(emojis_path, image))
                ])

    async def config_emojis(self, nayul: 'NayulCore'):
        """
        Configura todos os emojis e atualiza a classe Emoji.
        """
        
        log.warning('Iniciando configuração de emojis...')
        self.existing_emojis = {emoji.name: emoji for emoji in await nayul.fetch_application_emojis()}
        
        try:
            await self._get_emojis(nayul)
        except Exception:
            log.exception('Erro ao buscar emojis da API/GitHub/local')
            await nayul.close()
        
        await self.__generate_emoji_class(self.emojis_data)
