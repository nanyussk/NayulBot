import logging

import discord
from discord.ext import commands
from discord.app_commands.errors import (
	BotMissingPermissions,
	MissingPermissions,
)

from src import NayulCore
from src.utils.emojis import Emoji
from src.utils.others import Permissions


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class GlobalErrorHandler(commands.Cog):
	def __init__(self, nayul: NayulCore):
		"""Classe que trata os erros dos comandos do bot."""
		self.nayul = nayul
		self.nayul.tree.on_error = self.on_app_command_error

	def _format_permissions(self, missing: list[str], *, bot: bool) -> str:
		# Mapeia os nomes das permissões para descrições amigáveis.
		_P = Permissions()
		perms = '\n'.join(sorted([_P.get(name) for name in missing if _P.get(name)]))
		if not perms:
			return f'{Emoji.error} Permissões insuficientes para executar este comando.'

		if len(perms.splitlines()) == 1:
			return (
				f'{Emoji.error} {"Preciso" if bot else "Permissão insuficiente! Você precisa"} da seguinte permissão para esse comando:\n'
				f'**{perms}**'
			)

		return (
			f'{Emoji.error} {"Preciso" if bot else "Permissão insuficiente! Você precisa"} das seguintes permissões para esse comando:\n'
			f'**{perms}**'
		)
		
	async def on_app_command_error(self, inter: discord.Interaction[NayulCore], error: Exception):
		"""Função que trata os erros dos comandos do bot"""
		if inter.command is not None: #Verifica se o comando existe (para não dar erro 404)
			if inter.command._has_any_error_handlers():
				return None
		
		if isinstance(error, MissingPermissions): #Tratamento do erro de permissão do usuário.
			message = self._format_permissions(error.missing_permissions, bot=False)
		elif isinstance(error, BotMissingPermissions): #Tratamento do erro de permissão dos bots.
			message = self._format_permissions(error.missing_permissions, bot=True)
		else: #Caso o erro não tenha um tratamento.
			message = (
				f'{Emoji.error} Ocorreu um erro inesperado ao executar.\n'
        		f'-# Se o problema persistir, reporte ao desenvolvedor.\n'
        		f'```{error}```'
			)
			log.exception('Erro no comando:', exc_info=error)
			
		if inter.response.is_done(): #Evita resposta duplicada quando o comando já respondeu.
			await inter.followup.send(message, ephemeral=True)
		else:
			await inter.response.send_message(message, ephemeral=True)

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: Exception):
		"""Função que trata os erros dos comandos do bot"""
		if isinstance(error, commands.NotOwner):
			log.info(f'{ctx.author.name} ({ctx.author.id}) tentou usar um comando de desenvolvedor.')
			return
		
		if isinstance(error, commands.CommandNotFound):
			log.info(f'Comando não encontrado: {ctx.message.content}')
			return
		
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.reply(f'⏱️ Calma aí! Você só pode usar esse comando de novo em `{error.retry_after:.1f}` segundos.', delete_after=10)
			return

		log.exception('Erro no comando:', exc_info=error)
async def setup(nayul: NayulCore):
	await nayul.add_cog(GlobalErrorHandler(nayul))
