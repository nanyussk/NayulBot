import logging

import discord
from discord.ext import commands

from src import NayulCore
from src.utils import nayul_decorators

log = logging.getLogger(__name__)

class ModCommands(commands.Cog):
    def __init__(self, nayul: NayulCore):
        self.nayul = nayul

    @commands.command(name='nban', description='Banir um usuário do bot.')
    @nayul_decorators.is_staff()
    async def nayulban(self, ctx: commands.Context[NayulCore], user: discord.User, *, reason: str = 'Nenhum motivo fornecido'):
        """ Comando para banir um usuário do bot."""
        settings = await self.nayul.db.settings.get_settings()

        # Lista de verificações com mensagens irônicas associadas
        checks = [
            (user.id == self.nayul.user.id, 'Sério? Você quer que eu me auto-ban? Que ideia genial! 😅'),
            (user.id == ctx.author.id, 'Dá vontade de deixar, mas ainda gosto de você. Não posso banir você mesmo! 😜'),
            (user.id in self.nayul.owner_ids, 'Só de você tentar isso já considero traição! 😤'),
            (user.id in settings.staffs, 'Melhor não mexer com quem te modera, né? 😉'),
            (user.bot, 'Bots não podem ser banidos, mas se pudessem, você seria o primeiro! 🤖'),
        ]

        for condition, message in checks:
            if condition:
                return await ctx.reply(message)

        user_data = await self.nayul.db.users.get_user(user)
        if not user_data.accepted_terms:
            return await ctx.reply('O usuário não tem uma conta registrada.', delete_after=60)
        if user_data.ban_status is not None:
            return await ctx.reply(f'O usuário {user.mention} já está banido.', allowed_mentions=discord.AllowedMentions.none())

        await self.nayul.db.users.update_ban(user, True, ctx.author.id, reason)
        await ctx.send(f'{ctx.author.mention} **|** Usuário banido com sucesso!')
        log.info(f'Usuário {user.id} banido por {ctx.author.id} com motivo: {reason}')

    @commands.command(name='nunban', description='Desbanir um usuário do bot.')
    @nayul_decorators.is_staff()
    async def nayulunban(self, ctx: commands.Context[NayulCore], user: discord.User):
        """ Comando para desbanir um usuário do bot."""
        user_data = await self.nayul.db.users.get_user(user)
        if not user_data.accepted_terms:
            return await ctx.reply('O usuário não tem uma conta registrada.', delete_after=60)
        if user_data.ban_status is None:
            return await ctx.reply(f'O usuário {user.mention} não está banido.', allowed_mentions=discord.AllowedMentions.none(), delete_after=60)

        await self.nayul.db.users.update_ban(user, False)
        await ctx.send(f'{ctx.author.mention} **|** Usuário desbanido com sucesso!')
        log.info(f'Usuário {user.id} desbanido por {ctx.author.id}')

        # Tenta reutilizar um convite permanente para evitar criar varios.
        try:
            message = (
                '✅ Você foi **desbanido pela equipe** e agora pode usar todas as minhas funcionalidades novamente.\n'
                'Não desperdice essa segunda chance tá! 😉'
            )
            await user.send(message)
        except discord.Forbidden:
            log.warning(f'Não foi possível enviar mensagem privada para o usuário {user.id}.')

    @commands.command(name='serverinvite', description='Cria um convite para o servidor.')
    @nayul_decorators.is_staff()
    async def serverinvite(self, ctx: commands.Context[NayulCore], guild_id: int):
        """Cria um convite para o servidor."""
        guild = self.nayul.get_guild(guild_id)
        if not guild:
            return await ctx.reply('Servidor não encontrado.', delete_after=30)
        me = guild.me or guild.get_member(self.nayul.user.id)
        try:
            invites = await guild.invites()
            invite = next((invite for invite in invites if invite.max_age == 0 and invite.max_uses == 0), None)
        except discord.Forbidden:
            invite = None
        
        if not invite:
            for channel in guild.text_channels:
                if me and channel.permissions_for(me).create_instant_invite:
                    invite = await channel.create_invite(temporary=True)
                    break
        if not invite:
            return await ctx.reply(f'Não foi possível criar um convite para o servidor {guild.name}.', delete_after=30)
        
        await ctx.send(f'Convite para o servidor {guild.name}:\n{invite}', delete_after=300)
        log.info(f'Convite criado para o servidor {guild.name} ({guild.id}) por {ctx.author.id}')
        
async def setup(nayul: NayulCore):
    await nayul.add_cog(ModCommands(nayul))
    log.debug('Cog ModCommands carregado.')
