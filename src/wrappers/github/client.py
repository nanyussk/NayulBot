from __future__ import annotations

import aiohttp
from typing import Union

from .http import HTTPClient
from .data.repo import GitHubRepo
from .data.commit import GitHubCommit
from .data.file import GitHubFile
from .data.update_file import GitHubFileUpdateResponse
from .data.branch import GitHubBranch
from .data.entry import GitHubEntry

__all__ = ("HTTPClient",)

class Client:
    """
    Cliente principal para interagir com a API do GitHub.

    Fornece métodos para obter informações de repositórios e commits
    usando o cliente HTTP específico.

    Attributes:
        http (HTTPClient): Instância do cliente HTTP autenticado.
    """

    def __init__(self, token: str, *, session: aiohttp.ClientSession = None):
        """
        Inicializa o cliente com token de autenticação e sessão opcional.

        Args:
            token (str): Token de autenticação para a API do GitHub.
            session (aiohttp.ClientSession, opcional): Sessão HTTP reutilizável.
        """
        self.http = HTTPClient(token, session=session)

    async def get_repo_info(self, owner: str, repo: str) -> GitHubRepo:
        """
        Obtém informações públicas de um repositório específico.

        Args:
            owner (str): Nome do proprietário do repositório.
            repo (str): Nome do repositório.

        Returns:
            GitHubRepo: Objeto com os dados do repositório.
        """
        data = await self.http.get_repo_info(owner, repo)
        return GitHubRepo(**data)
    
    async def get_commits(self, owner: str, repo: str, *, branch: str = 'main', per_page: int = 25) -> list[GitHubCommit]:
        """
        Obtém uma lista dos commits recentes de uma branch do repositório.

        Args:
            owner (str): Nome do proprietário do repositório.
            repo (str): Nome do repositório.
            branch (str, opcional): Nome da branch (padrão é 'main').
            per_page (int, opcional): Número máximo de commits a retornar (padrão é 25).

        Returns:
            list[GitHubCommit]: Lista de objetos representando os commits.
        """
        data = await self.http.get_commits(owner, repo, branch=branch, per_page=per_page)
        return [GitHubCommit(**commit) for commit in data]

    async def get_file(self, owner: str, repo: str, path: str, branch: str = 'main') -> GitHubFile:
        """
        Busca o arquivo no repositório e retorna como model GitHubFile.

        Args:
            owner (str): Dono do repositório.
            repo (str): Nome do repositório.
            path (str): Caminho do arquivo no repositório.
            branch (str): Branch para buscar o arquivo. Padrão é 'main'.

        Returns:
            GitHubFile: Model com dados do arquivo.
        """
        data = await self.http.get_file_content(owner, repo, path, branch=branch)
        if isinstance(data, list) or 'content' not in data:
            raise ValueError(f'O caminho "{path}" não é um arquivo válido ou está inacessível.')
        return GitHubFile(**data)
    
    async def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        commit_message: str,
        content: str,
        sha: str,
        branch: str = 'main'
    ) -> GitHubFileUpdateResponse:
        """
        Atualiza um arquivo existente em um repositório.

        Args:
            owner (str): Nome do dono do repositório.
            repo (str): Nome do repositório.
            path (str): Caminho do arquivo a ser atualizado.
            commit_message (str): Mensagem do commit.
            content (str): Novo conteúdo do arquivo.
            sha (str): SHA do arquivo atual (necessário para update).
            branch (str, opcional): Nome da branch. Default: 'main'.

        Returns:
            GitHubFileUpdateResponse: Dados do conteúdo atualizado e commit.
        """
        data = await self.http.update_file(
            owner,
            repo,
            path,
            commit_message,
            content,
            sha,
            branch=branch
        )
        return GitHubFileUpdateResponse(**data)

    async def get_branches(self, owner: str, repo: str) -> list[GitHubBranch]:
        """
        Obtém a lista de branches do repositório e retorna como modelos `GitHubBranch`.

        Args:
            owner (str): Nome do dono do repositório.
            repo (str): Nome do repositório.

        Returns:
            list[GitHubBranch]: Lista de objetos representando as branches.
        """
        data = await self.http.get_branches(owner, repo)
        return [GitHubBranch(**branch) for branch in data]
    
    async def get_branch(self, owner: str, repo: str, branch: str = 'main') -> GitHubBranch:
        """
        Obtém os dados de uma branch específica.

        Args:
            owner (str): Nome do dono do repositório.
            repo (str): Nome do repositório.
            branch (str, opcional): Nome da branch. Default: 'main'.

        Returns:
            GitHubBranch: Objeto representando a branch.
        """
        data = await self.http.get_branch(owner, repo, branch=branch)
        return GitHubBranch(**data)
    
    async def list_directory_or_get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str = 'main'
    ) -> Union[list[GitHubEntry], GitHubFile]:
        """
        Lista o conteúdo de um diretório ou retorna o arquivo, caso o caminho seja um arquivo.

        Returns:
            - Lista de GitHubEntry se for diretório
            - GitHubFile se for arquivo
        """
        data = await self.http.list_directory(owner, repo, path, branch)
    
        if isinstance(data, list):
            # Diretório: lista de arquivos/pastas
            return [GitHubEntry(**entry) for entry in data]
        else:
            # Arquivo: dados completos com conteúdo
            return GitHubFile(**data)

    async def list_all_path_files(self, owner: str, repo: str, path: str = '.', branch: str = 'main') -> list[str]:
        """
        Lista recursivamente todos os arquivos de um diretório ou do repositório inteiro caso `path` seja vazio.
        Utiliza o método `list_directory` para obter o conteúdo e percorre subdiretórios recursivamente.

        Args:
            owner (str): Dono do repositório.
            repo (str): Nome do repositório.
            path (str, opcional): Caminho inicial para listagem. Padrão é '.' (raiz).
            branch (str, opcional): Branch para referência. Padrão é 'main'.

        Returns:
            List[str]: Lista de paths completos de todos os arquivos encontrados.
        """
        all_files: list[str] = []

        async def walk(current_path: str):
            entries = await self.list_directory_or_get_file(owner, repo, current_path, branch)
            for entry in entries:
                if entry.type == 'file':
                    all_files.append(entry.path)
                elif entry.type == 'dir':
                    await walk(entry.path)

        await walk(path)
        return all_files
