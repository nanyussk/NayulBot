import logging
from motor.motor_asyncio import AsyncIOMotorClient

from src.env import ENV
from src.database.user_db import UsersDB
from src.database.skin_db import SkinsDB
from src.database.settings_db import SettingsDB

log = logging.getLogger(__name__)

class DatabaseClient:
    """
    Gerencia a conexão com o banco de dados MongoDB.
    """
    def __init__(self, **kwargs):
        self.users: UsersDB = kwargs.get('users')
        self.skin: SkinsDB = kwargs.get('skin')
        self.settings: SettingsDB = kwargs.get('settings')


    @classmethod
    async def connect(cls) -> 'DatabaseClient':
        """
        Conecta ao banco de dados MongoDB.

        Returns:
            DatabaseClient: Uma instância da classe DatabaseClient.
        """
        try:
            client = AsyncIOMotorClient(ENV.MONGO)
            return cls(
                users=UsersDB(client),
                skins=SkinsDB(client),
                settings=SettingsDB(client)
            )
            log.debug('Conectado ao MongoDB com sucesso.')
        except Exception:
            log.critical('Não foi possível conectar ao MongoDB.', exc_info=True)
            raise ConnectionError('Não foi possível conectar ao MongoDB.')