import discord
import logging
from functools import wraps
from discord.ext import commands
from typing import Union

from src import NayulCore
from .others import format_timestamp, Colors

log = logging.getLogger(__name__)

def is_staff():
    """Verifica se o usuário é um staff do bot."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context[NayulCore], *args, **kwargs):
            settings = await ctx.bot.db.settings.get_settings()
            if ctx.author.id in settings.staffs or ctx.author.id in ctx.bot.owner_ids:
                return await func(self, ctx, *args, **kwargs)
            log.debug('Acesso staff negado user_id=%s', ctx.author.id)
        return wrapper
    return decorator

def check_user_banned():
    """Verifica se o usuário está banido do bot."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, inter: Union[discord.Interaction, discord.Message], *args, **kwargs):
            if isinstance(inter, discord.Interaction):
                user = inter.user
                nayul: NayulCore = inter.client
            else:
                user = inter.author
                nayul: NayulCore = self.nayul
            
            user_data = await nayul.db.users.get_user(user)

            if user_data.ban_status:
                log.info('Usuario banido bloqueado user_id=%s', user.id)
                if isinstance(inter, discord.Interaction):
                    banned_at = user_data.ban_status.banned_at
                    embed = discord.Embed(
                        title='Você está banido!',
                        color=Colors.MYSTIC_PURPLE,
                        description=(
                            f'Olá {inter.user.mention}, sua conta foi **banida** e não poderá utilizar nenhuma funcionalidade da {self.nayul.user.name}.\n\n'
                            f'**Banido em:** {format_timestamp(banned_at, "F")} ({format_timestamp(banned_at, "R")})\n'
                            f'**Motivo:** {user_data.ban_status.reason}\n'
                        )
                    ).set_thumbnail(url=inter.user.display_avatar.url)
                    embed.set_footer(text='Se você acredita que isso é um erro, entre em contato com a equipe do bot.')
                    await inter.response.send_message(
                        embed=embed,
                        ephemeral=True,
                        allowed_mentions=discord.AllowedMentions.none()
                    )
                return

            return await func(self, inter, *args, **kwargs)
        return wrapper
    return decorator
