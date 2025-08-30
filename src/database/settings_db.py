from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal
import logging

from src.database.models.settings import Settings

log = logging.getLogger(__name__)

class SettingsDB:
    def __init__(self, client: AsyncIOMotorClient):
        self.collection = client['nayul']['settings']

    async def get_settings(self) -> Settings:
        """
        Obtém as configurações do bot do banco de dados.

        Returns:
            Settings: As configurações do bot.
        """
        data = await self.collection.find_one({'_id': 0})
        if data is None:
            default_settings = Settings().to_dict()
            default_settings['_id'] = 0
            await self.collection.insert_one(default_settings)
            log.debug('Configurações padrão inseridas no banco de dados.')
            return Settings()
        
        log.debug('Settings: %s', data)
        return Settings(**data)

    async def update_settings(self, *, query: dict) -> None:
        """
        Atualiza as configurações do bot no banco de dados.

        Args:
            query (`dict`): Os dados a serem atualizados.
        """
        await self.collection.update_one({'_id': 0}, query, upsert=True)
        log.debug('Configurações atualizadas no banco de dados.')

    async def update_staffs(self, action: Literal['add', 'remove'], staff_id: int) -> None:
        """
        Atualiza a lista de staffs do bot no banco de dados.

        Args:
            action (`Literal['add', 'remove']`): A ação a ser realizada.
            staff_id (`int`): O ID do staff a ser adicionado ou removido.
        """
        settings = await self.get_settings()
        settings_dict = settings.to_dict()

        match action:
            case 'add':
                if staff_id not in settings_dict['staffs']:
                    settings_dict['staffs'].append(staff_id)
            case 'remove':
                if staff_id in settings_dict['staffs']:
                    settings_dict['staffs'].remove(staff_id)

        await self.update_settings(query={'$set': settings_dict})
        log.debug('Staff %s: %s', action, staff_id)