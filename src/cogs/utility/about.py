import platform
import time
from datetime import timedelta

import discord
import psutil
from discord import app_commands
from discord.ext import commands
import logging

import src
from src import NayulCore
from src.utils import nayul_decorators
from src.utils.others import Colors

log = logging.getLogger(__name__)

class AboutBot(commands.Cog):
    """Classe que contém os comandos de utilidade do bot."""

    def __init__(self, nayul: NayulCore):
        self.nayul: NayulCore = nayul

    @app_commands.command(
        name="ping", description="Mostra informações sobre a latência do bot."
    )
    @nayul_decorators.check_user_banned()
    async def ping(self, inter: discord.Interaction[NayulCore]):
        """Comando que verifica a latência do bot."""
        log.info('Comando /ping user_id=%s', inter.user.id)

        # Mede o tempo de ida e volta entre a interação e a resposta.
        start = time.perf_counter()
        await inter.response.send_message("🏓 | Ping...")
        end = time.perf_counter()

        ws_latency = round(inter.client.latency * 1000)
        api_latency = round((end - start) * 1000)

        await inter.edit_original_response(
            content=f"🏓 | Pong!\n**Latência do WebSocket:** {ws_latency}ms\n**Latência da API:** {api_latency}ms\n"
        )

    @app_commands.command(name="botinfo", description="Mostra informações sobre o bot.")
    @nayul_decorators.check_user_banned()
    async def botinfo(self, inter: discord.Interaction[NayulCore]):
        """Comando que mostra informações sobre o bot."""
        log.info('Comando /botinfo user_id=%s', inter.user.id)

        client = inter.client
        embed = discord.Embed(
            title=f"Informações sobre {client.user.name}",
            color=Colors.MYSTIC_PURPLE,
        )
        embed.description = (
            f"```yaml\n"
            f"SO:               {platform.system()} {platform.release()}\n"
            f"Python:           {platform.python_version()}\n"
            f"Discord.py:       {discord.__version__}\n"
            f"Versão:           {src.__version__}\n"
            f"```"
        )
        embed.set_thumbnail(url=client.user.display_avatar.url)

        embed.add_field(
            name="📊 Estatísticas",
            value=(
                f"**Servidores:** `{len(client.guilds)}`\n"
                f"**Usuários:** `{len(set(client.users))}`\n"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚙️ Desempenho",
            value=(
                f"**Uptime:** `{str(timedelta(seconds=int(time.time() - client.uptime)))}`\n"
                f"**Latência:** `{round(client.latency * 1000)}ms`\n"
                f"**CPU:** `{psutil.cpu_percent()}%`\n"
                f"**Memória:** `{round(psutil.virtual_memory().percent, 2)}%`"
            ),
            inline=False,
        )

        owner = client.get_user(list(client.owner_ids)[0])
        if owner is None:
            # Evita erro caso o owner ainda nao esteja em cache.
            owner_text = "Desenvolvida pela equipe"
            owner_avatar = client.user.display_avatar.url
        else:
            owner_text = f"Desenvolvida por {owner.name} ({owner.id})"
            owner_avatar = owner.display_avatar.url

        embed.set_footer(
            text=owner_text,
            icon_url=owner_avatar,
        )

        await inter.response.send_message(embed=embed, ephemeral=True)


async def setup(nayul: NayulCore):
    await nayul.add_cog(AboutBot(nayul))
    log.debug('Cog AboutBot carregado.')
