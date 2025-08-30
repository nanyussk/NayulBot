from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Literal, List
import logging

from src.database.models.skin import ProfileSkin

log = logging.getLogger(__name__)

class SkinsDB:
    def __init__(self, client: AsyncIOMotorClient):
        self.collection = client['nayul']['skins']

    async def get_skins(self) -> list[ProfileSkin]:
        """
        Obtém as skins de perfil do banco de dados.

        Returns:
            list[ProfileSkin]: As skins de perfil.
        """
        data: Optional[list[dict]] = await self.collection.find().to_list(length=None)
        if data is None:
            log.debug('Nenhuma skin encontrada no banco de dados.')
            return []
        log.debug('Skins encontradas: %s', data)
        return [ProfileSkin(**skin) for skin in data]
    
    async def get_skin(self, skin_id: str) -> Optional[ProfileSkin]:
        """
        Obtém uma skin de perfil do banco de dados.

        Args:
            skin_id (`str`): O ID da skin a ser obtida.

        Returns:
            ProfileSkin: A skin de perfil.
        """
        data: Optional[dict] = await self.collection.find_one({'_id': skin_id})
        if data is None:
            log.debug('Skin não encontrada com o ID: %s', skin_id)
            return None
        log.debug('Skin encontrada: %s', data)
        return ProfileSkin(**data)
    
    async def remove_skin(self, skin_id: str) -> None:
        """
        Remove uma skin de perfil do banco de dados.

        Args:
            skin_id (`str`): O ID da skin a ser removida.
        """
        await self.collection.delete_one({'_id': skin_id})
        log.debug('Skin removida com o ID: %s', skin_id)

    async def add_skin(self, skin_id: str, name: str, rarity: Literal[0, 1, 2, 3, 4], price: int, url: str, description: Optional[str] = None, author: Optional[str] = None) -> None:
        """
        Adiciona uma nova skin de perfil ao banco de dados.

        Args:
            skin_id (`str`): O ID da nova skin.
            name (`str`): Nome da skin.
            price (`int`): Preço da skin em pérolas.
            rarity (`Literal[0, 1, 2, 3, 4]`): Raridade da skin.
            description (`Optional[str]`): Descrição da skin.
            author (`Optional[str]`): Autor da skin.
            url (`str`): URL da imagem da skin.
        """
        skin_dict = ProfileSkin(
            id=skin_id,
            name=name,
            price=price,
            rarity=rarity,
            description=description,
            author=author,
            url=url
        ).to_dict()
        await self.collection.insert_one(skin_dict)
        log.debug('Skin %s adicionada com os dados: %s', skin_dict)

    async def update_skin(self, skin_id: str, *, name: Optional[str] = None, rarity: Optional[Literal[0, 1, 2, 3, 4]] = None, price: Optional[int] = None, description: Optional[str] = None, author: Optional[str] = None, url: Optional[str] = None,) -> None:
        """
        Atualiza uma skin de perfil no banco de dados.

        Args:
            skin_id (`str`): O ID da skin a ser atualizada.
            name (`Optional[str]`): Novo nome da skin.
            price (`Optional[int]`): Novo preço da skin em pérolas.
            rarity (`Optional[Literal[0, 1, 2, 3, 4]]`): Nova raridade da skin.
            description (`Optional[str]`): Nova descrição da skin.
            url (`Optional[str]`): Nova URL da imagem da skin.

        Raises:
            ValueError: Se nenhum valor for fornecido para atualização.
            ValueError: Se a skin não for encontrada com o ID fornecido.
        """
        
        skin_data = await self.get_skin(skin_id)
        if skin_data is None:
            raise ValueError('Skin não encontrada com o ID fornecido.')

        skin_dict = ProfileSkin(
            id=skin_data.id,
            name=name or skin_data.name,
            price=price or skin_data.price,
            rarity=rarity or skin_data.rarity,
            description=description or skin_data.description,
            author=author or skin_data.author,
            url=url or skin_data.url
        ).to_dict()

        await self.collection.update_one({'_id': skin_id}, {'$set': skin_dict})
        log.debug('Skin %s atualizada com os dados: %s', skin_dict)

    async def get_all_skins(self) -> List[ProfileSkin]:
        """Pega todas as skins do banco de dados.
        Returns:
            List[ProfileSkin]: Lista de todas as skins.
        """

        skins = []
        async for skin in self.collection.find().to_list(length=None):
            skins.append(ProfileSkin(**skin))
        return skins