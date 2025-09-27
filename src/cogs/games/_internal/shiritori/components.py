import discord
from discord import ui

import time
import logging
import asyncio
from typing import Set

from src import NayulCore
from src.utils.emojis import Emoji
from .utils import configure_player_button
from .gameflow import start_game_shiritori
from .views import ConfirmPlayer, SelectPlayers, ConfirmStartGame

log = logging.getLogger(__name__)

#View principal (components v2)
class MainView(ui.LayoutView):
    def __init__(self, author: discord.Member, players: Set[discord.Member]):
        super().__init__(timeout=300)
        self.start_time: int = int(time.time() + 120) #Tempo para o iniciar a partida em timestamp
        self.auto_start: bool = True #Se iniciar automáticamente está ativo ou não
        self.author: discord.Member = author #Autor da partida (quem executou o comando)
        self.players: Set[discord.Member] = players #Lista com os jogadores (sem confirmação)
        self.confirmed_players: Set[discord.Member] = set() #Lista com os jogadores (que irão jogar)
        self.start_game = start_game_shiritori #Função para iniciar a partida
        self.container: ui.Container = Container(self)

        #Adicionando o item a view
        self.add_item(self.container)
        self.confirm_button = ConfirmStartGame(self)
        self.add_item(ui.ActionRow(*[self.confirm_button]))

    async def disable_all_items(self):
        """Desativa todos os botões da view."""

        #Desativa todos os botões no container
        for item in self.container.children:
            if isinstance(item, ui.Section) and isinstance(item.accessory, ConfirmPlayer):
                item.accessory.disabled = True
            elif isinstance(item, ui.ActionRow):
                for subitem in item.children:
                    if isinstance(subitem, SelectPlayers):
                        subitem.disabled = True

        #Desativa os que estão fora do container
        for child in self.children:
            if isinstance(child, ui.ActionRow):
                for subchild in child.children:
                    if isinstance(subchild, ConfirmStartGame):
                        subchild.disabled = True
            elif isinstance(child, ConfirmStartGame):
                child.disabled = True

    async def start_game_auto(self, inter: discord.Interaction[NayulCore]):
        """Inicia a partida automaticamente.

        Args:
            inter (discord.Interaction): Interação do usuário.

        Raises:
            Exception: Erro ao iniciar a partida.
        """
        try:
            await asyncio.sleep(120)

            if not self.auto_start: 
                return # Retorna caso já tenha iniciado a partida
            
            await self.disable_all_items()
            await inter.edit_original_response(
                view=self,
                allowed_mentions=discord.AllowedMentions(
                    users=False,
                    roles=False,
                    everyone=False
                )
            )

            if len(self.confirmed_players) < 2:
                await inter.followup.send(
                    '⏰ Tempo de espera esgotado! Não é possível iniciar a partida com menos de 2 jogadores.'
                )
                return
            
            await self.start_game(self, inter)            
        except Exception as e:
            #Loga o erro
            log.error('Erro em start_game_auto:', exc_info=e)
           

#Container com informações, imagens, botões e menu de seleção(membros)
class Container(ui.Container):
    def __init__(self, view: MainView):
        super().__init__(accent_color=0x223f4f)

        #Banner do jogo com os créditos
        self.add_item(
            ui.MediaGallery(
                discord.components.MediaGalleryItem(
                    media='https://i.postimg.cc/Zq7wyntv/shiritori-banner.png',
                    description='Banner do jogo Shiritori by arrthur_.'
                )
            )
        )
        # Instruções do jogo
        self.add_item(
            ui.TextDisplay(
                ''.join(
                    [
                        'Os jogadores devem digitar uma palavra que comece com as duas últimas letras da palavra dita pelo jogador anterior. Verificarei se a palavra é válida e continua o jogo. Aqui está um exemplo:\n',
                        '> Abel**ha** -> **Ha**mster\n\n',
                    ]
                )
            )
        )
        # Separador visual
        self.add_item(
            ui.Separator()
        )
        # Lista de jogadores e convite
        self.add_item(
            ui.TextDisplay(
                ''.join(
                    [
                        f'### Jogadores ({len(view.players)}/25)\n',
                        f'-# **{view.author.display_name}** convidou você para uma partida de Shiritori.\n',
                        '-# Clique em **Aceitar** para confirmar sua participação!'
                    ]
                )
            )
        )
        # Adiciona um botão de confirmação para cada jogador
        for player in view.players:
            display_name = f'{Emoji.crown} {player.mention}' if player == view.author else f'{Emoji.icon_user} {player.mention}'
            button_confirm = ConfirmPlayer(view, player.id)
            #Verifica se o jogador já confirmou sua participação, caso seja `True` ele edita o botão
            if player in view.confirmed_players:
                configure_player_button(button_confirm)

            self.add_item(
                ui.Section(
                    f'{display_name} - `{player.id}`',
                    accessory=button_confirm
                )
            )
        self.add_item(
            ui.Separator()
        )
        # Adiciona o menu de seleção de jogadores
        self.add_item(
            ui.ActionRow(SelectPlayers(view))
        )
        # Mensagem de tempo limite para confirmação
        self.add_item(
            ui.TextDisplay(
                f'-# ⏳ Os jogadores têm até <t:{view.start_time}:T> (<t:{view.start_time}:R>) para confirmar sua participação.'
            )
        )
        
