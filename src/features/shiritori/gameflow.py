import asyncio
import logging
import random
import time
from datetime import datetime
from typing import TYPE_CHECKING

import discord
from unidecode import unidecode

if TYPE_CHECKING:
    from .components import MainView

from src import NayulCore
from src.utils.emojis import Emoji
from .utils import (
    validate_word_shiritori,
    get_time_limit,
    get_phase_message,
    update_player_stats,
    create_stats_dict
)

log = logging.getLogger(__name__)

# Inicia a partida
async def start_game_shiritori(view: 'MainView', inter: discord.Interaction[NayulCore]):
    """Inicia a partida de Shiritori.

    Args:
        view (`MainView`): View principal da partida.
        inter (`discord.Interaction`): Interação do usuário.

    Raises:
        Exception: Erro ao iniciar a partida ou durante o jogo.
    """
    if inter.channel is None:
        return

    channel = inter.channel
    players = list(view.confirmed_players)
    used_words = set()
    previous_word = None
    start_time_game = datetime.now() # Hora que a partida iniciou
    players_stats = create_stats_dict(players) # Cria um dicionário de estatísticas dos jogadores
    random.shuffle(players) # Embaralha a lista de jogadores
    players_mentions = ', '.join([p.mention for p in players])
    log.info('Shiritori iniciado channel_id=%s players=%s', channel.id, len(players))

    await channel.send(
        content=f'⚠️ A partida irá começar <t:{int(time.time()) + 10}:R>!\n🎮 Jogadores: {players_mentions}',
        delete_after=10
    )
    await asyncio.sleep(10)

    while len(players) > 1: # O loop só acaba quando restar somente 1 jogador
        for player in players.copy():
            if len(players) == 1:
                break

            time_limit = get_time_limit(len(used_words)) # Tempo limite para responder baseado no número de palavras já usadas
            ends_at = int(time.time() + time_limit)
            start_turn = datetime.now()

            # Monta o embed de espera do turno, com instruções e tempo restante
            if previous_word:
                phase_msg = get_phase_message(time_limit, ends_at)
                embed_waiting = discord.Embed(
                    description=(
                        f'Digite uma palavra que comece com as duas últimas letras de:\n'
                        f'### **{previous_word[:-2]}**__**{previous_word[-2:]}**__\n\n'
                        f'{phase_msg}'
                    ),
                    color=discord.Color.blurple()
                ).set_footer(text=f'Palavra #{len(used_words)}')
            else:
                # Primeiro turno: instrução inicial
                embed_waiting = discord.Embed(
                    title='Início do Jogo',
                    description='Digite a primeira palavra para começar!',
                    color=discord.Color.blurple()
                )
            # Envia a mensagem para o jogador atual
            message_player = await channel.send(
                content=player.mention,
                embed=embed_waiting,
            )

            while True:
                try:
                    # Calcula o tempo restante para o jogador responder
                    remaining_time = time_limit - (datetime.now() - start_turn).total_seconds()
                    if remaining_time <= 0:
                        raise asyncio.TimeoutError()
                    
                    # Aguarda a mensagem do jogador dentro do tempo limite
                    message = await inter.client.wait_for(
                        'message',
                        timeout=remaining_time,
                        check=lambda m: m.author == player and m.channel == channel
                    )
                    word = unidecode(message.content.lower().strip())

                    # Valida se a palavra começa com as duas últimas letras da anterior
                    if previous_word and not word.startswith(previous_word[-2:]):
                        continue

                    # Elimina o jogador se a palavra já foi usada
                    if word in used_words:
                        embed = discord.Embed(
                            title='Palavra Repetida!',
                            description=f'{Emoji.error} {player.mention}, a palavra **{word}** já foi usada. Você foi eliminado.',
                            color=discord.Color.red()
                        )
                
                        await message_player.delete()
                        await channel.send(embed=embed)
                        players.remove(player)
                        update_player_stats(players_stats, player.id, 'end')
                        break

                    # Valida se a palavra é aceita pelo jogo
                    valid = validate_word_shiritori(word)
                    if not valid:
                        continue

                    # Palavra válida: adiciona à lista, marca como usada e avança o turno
                    used_words.add(word)
                    previous_word = word
                    update_player_stats(players_stats, player.id, 'words_list', word)
                    await message.add_reaction(Emoji.check)
                    await message_player.delete()
                    break

                except asyncio.TimeoutError:
                    # Elimina o jogador por não responder a tempo
                    embed_timeout = discord.Embed(
                        title='Tempo Esgotado!',
                        description=(
                            f'⏰ {player.mention} não respondeu a tempo (**{time_limit}s**).\n'
                            'Você foi eliminado.'
                        ),
                        color=discord.Color.red()
                    )
                    await message_player.delete()
                    await channel.send(embed=embed_timeout)
                    players.remove(player)
                    update_player_stats(players_stats, player.id, 'end')
                    break
                except Exception as e:
                    #Loga o erro para debug
                    log.error('Erro em start_game_shiritori:', exc_info=e)

    player_winner = players[0]
    end_time_game = datetime.now() # Hora que a partida terminou
    update_player_stats(players_stats, player_winner.id, 'end', end_time_game)

    embed = discord.Embed(
        title='🏁 Resultado da Partida de Shiritori',
        color=discord.Color.gold(),
        url=inter.message.jump_url
    )
    embed.set_thumbnail(url=player_winner.display_avatar.url)
    embed.add_field(name='🏆 Vencedor:', value=player_winner.mention, inline=False)
    embed.add_field(name='📊 Palavras usadas:', value=f'```{len(used_words)}```', inline=False)
    embed.add_field(name='⏱️ Duração da Partida:', value=f'```{str(end_time_game - start_time_game).split(".")[0]}```', inline=False)

    from .views import PlayerStatusSelectView # Evitar importação circular
    await channel.send(embed=embed, view=PlayerStatusSelectView(players_stats))
    log.info('Shiritori finalizado channel_id=%s winner_id=%s', channel.id, player_winner.id)
