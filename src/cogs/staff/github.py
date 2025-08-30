from discord.ext import commands

import base64
from typing import List

from src import NayulCore
from src.env import ENV
from src.utils import nayul_decorators
from src.wrappers.github.client import Client as GitHubClient
from src.wrappers.github.data.file import GitHubFile

REPO_NAME = 'NayulCoreAPI'
WORDS_PATH = 'files/words/wordle/pt.txt'

class GitHubCommands(commands.Cog):
    def __init__(self, nayul: NayulCore):
        self.nayul = nayul
        self.client = GitHubClient(ENV.GITHUB_TOKEN, session=self.nayul.session)

    @commands.group(name='wordle', invoke_without_command=True)
    @nayul_decorators.is_staff()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def wordle(self, ctx: commands.Context[NayulCore]):
        """Mostra ajuda do grupo *wordle* se nenhum subcomando for passado."""
        if not ctx.invoked_subcommand:
            prefix = ENV.PREFIX
            await ctx.reply(f'Use `{prefix}wordle add <palavras>`, `{prefix}wordle remove <palavras>` ou `{prefix}wordle list` para gerenciar as palavras do Wordle.')

    @wordle.command(name='add', description='Adiciona palavras ao wordle.')
    @nayul_decorators.is_staff()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def words_add(self, ctx: commands.Context, *words: str) -> None:
        """Adiciona novas palavras de 5 letras ao arquivo remoto."""

        if ctx.author.id in self.nayul.owner_ids:
            ctx.command.reset_cooldown(ctx)
            
        if not words:
            await ctx.send('⚠️ Você deve fornecer ao menos uma palavra de 5 letras.')
            return

        adicionadas = await self._edit_words(add=list(words), author=str(ctx.author))
        if adicionadas:
            await ctx.send(f'✅ Adicionadas {len(adicionadas)} palavra(s): {", ".join(adicionadas)}')
        else:
            await ctx.send('🤔 Nenhuma palavra nova foi adicionada (já existiam ou eram inválidas).')

    @wordle.command(name='remove', description='Remove palavras do wordle.')
    @nayul_decorators.is_staff()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def words_remove(self, ctx: commands.Context, *words: str) -> None:
        """Remove palavras do arquivo remoto."""

        if ctx.author.id in self.nayul.owner_ids:
            ctx.command.reset_cooldown(ctx)

        if not words:
            await ctx.send('⚠️ Você deve fornecer ao menos uma palavra para remover.')
            return

        removidas = await self._edit_words(remove=list(words), author=str(ctx.author))
        if removidas:
            await ctx.send(f'🗑️ Removidas {len(removidas)} palavra(s): {", ".join(removidas)}')
        else:
            await ctx.send('🤔 Nenhuma das palavras fornecidas estava na lista.')

    @wordle.command(name='list', description='Lista todas as palavras do wordle no arquivo remoto.')
    @nayul_decorators.is_staff()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def words_list(self, ctx: commands.Context) -> None:
        """Lista todas as palavras de 5 letras no arquivo remoto."""
        try:
            await ctx.author.send(f'💌 **|** Aqui está o arquivo com as palavras: {ENV.INTERNAL_API}words/wordle/pt.txt')
            await ctx.send('😉 **|** Te enviei a lista no privado! Não compartilha por aí, viu?', delete_after=30)
        except Exception:
            await ctx.send('🙄 **|** Tentei mandar no privado, mas parece que sua DM está mais fechada que meu coração pra quem usa Comic Sans.', delete_after=30)

    async def _edit_words(self, add: list[str] = None, remove: list[str] = None, author: str = 'nayul') -> list[str]:
        """Carrega o arquivo, aplica alterações e commita.

        Retorna lista de palavras efetivamente adicionadas ou removidas.
        """
        assert self.client is not None, 'GitHub client não inicializado'

        # 1. Buscar arquivo e SHA atual
        try:
            file: GitHubFile = await self.client.get_file(ENV.GITHUB_USERNAME, REPO_NAME, WORDS_PATH)
            sha = file.sha
            raw_content = base64.b64decode(file.content).decode('utf-8')
        except Exception as exc:
            raise RuntimeError(f'Falha ao carregar {WORDS_PATH}: {exc}') from exc

        words_set = {w.strip().lower() for w in raw_content.splitlines() if w.strip() and len(w.strip()) == 5}

        added: List[str] = []
        removed: List[str] = []

        # 2. Adicionar
        if add:
            for w in add:
                w = w.lower()
                if len(w) == 5 and w not in words_set:
                    words_set.add(w)
                    added.append(w)

        # 3. Remover
        if remove:
            for w in remove:
                w = w.lower()
                if w in words_set:
                    words_set.remove(w)
                    removed.append(w)

        # Nenhuma mudança?
        if not added and not removed:
            return []

        # 4. Conteúdo final ordenado
        final_content = '\n'.join(sorted(words_set)) + '\n'

        # 5. Commit
        commit_msg_parts = []
        if added:
            commit_msg_parts.append(f'add {len(added)} word(s)')
        if removed:
            commit_msg_parts.append(f'remove {len(removed)} word(s)')
        commit_message = f'words: {", ".join(commit_msg_parts)} (by {author})'

        await self.client.update_file(
            owner=ENV.GITHUB_USERNAME,
            repo=REPO_NAME,
            path=WORDS_PATH,
            commit_message=commit_message,
            content=final_content,
            sha=sha
        )

        if added:
            self.nayul.word_manager.five_letter_words.update(added)
        else:
            self.nayul.word_manager.five_letter_words.difference_update(removed)

        return added if added else removed

async def setup(nayul: NayulCore):
    await nayul.add_cog(GitHubCommands(nayul))