import discord
from discord.ext import commands
from discord import app_commands

from src import NayulCore
from src.utils import nayul_decorators
from ._internal.shiritori import MainView as MainViewShiritori

class PlayGames(commands.Cog):
    def __init__(self, nayul: NayulCore):
        self.nayul = nayul

    play = app_commands.Group(
        name='jogar',
        description='Grupo de comandos para iniciar e interagir com jogos divertidos.',
        guild_only=True
    )

    @play.command(name='shiritori', description='Forme palavras começando com a última letra da anterior.')
    @app_commands.checks.bot_has_permissions(
        embed_links=True,
        send_messages=True,
        read_messages=True,
        add_reactions=True
    )
    @nayul_decorators.check_user_banned()
    async def shiritori(self, inter: discord.Interaction[NayulCore]):
        """Inicia uma partida de Shiritori."""
        players: set[discord.Member] = [inter.user]
        view = MainViewShiritori(inter.user,players)

        await inter.response.send_message(
            view=view, 
            allowed_mentions=discord.AllowedMentions(
                users=False,
                roles=False,
                everyone=False
        ))
        await view.start_game_auto(inter)

async def setup(nayul: NayulCore):
    await nayul.add_cog(PlayGames(nayul))
