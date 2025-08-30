import asyncio
import logging

from src.env import ENV
from src import NayulCore

class ColorizedHandler(logging.StreamHandler):
    COLORS = {
        'DEBUG': '\033[94m',     # Azul
        'INFO': '\033[92m',      # Verde
        'WARNING': '\033[93m',   # Amarelo
        'ERROR': '\033[91m',     # Vermelho
        'CRITICAL': '\033[95m',  # Roxo
    }
    RESET = '\033[0m'

    def emit(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        record.msg = f"{color}{record.msg}{self.RESET}"
        super().emit(record)


handler = ColorizedHandler()
formatter = logging.Formatter('%(name)s | %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger(__name__)

log.info('Iniciando o bot...')

# Inicia a aplicação.
async def main():
    async with NayulCore() as nayul:
        await nayul.start(ENV.TOKEN)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
except Exception:
    log.exception('Ocorreu um erro ao iniciar a aplicação:')