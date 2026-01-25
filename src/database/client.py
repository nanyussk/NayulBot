import logging
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import ENV
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
            log.debug('Conectado ao MongoDB com sucesso.')
            db = cls(
                users=UsersDB(client),
                skin=SkinsDB(client),
                settings=SettingsDB(client)
            )
            await db.create_indexes()
            return db
        except Exception:
            log.critical('Não foi possível conectar ao MongoDB.', exc_info=True)
            raise ConnectionError('Não foi possível conectar ao MongoDB.')

    async def create_indexes(self) -> None:
        log.debug('Criando indices do banco.')
        await self.users.create_indexes()
        await self.skin.create_indexes()
        await self.settings.create_indexes()
        log.debug('Indices criados.')
