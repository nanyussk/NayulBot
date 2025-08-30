from __future__ import annotations

import logging
import aiohttp
import base64

from .._base_http import BaseRouter, BaseHTTPClient

log = logging.getLogger(__name__)

class Router(BaseRouter):
    """
    Router para a API do GitHub.
    
    Define a URL base para todas as rotas da API.
    """
    BASE = 'https://api.github.com'


class HTTPClient(BaseHTTPClient):
    """
    Cliente HTTP para fazer requisições à API do GitHub.
    
    Herda de `BaseHTTPClient` e fornece métodos específicos para endpoints do GitHub.
    """
    DEFAULT_HEADERS = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'NayulBot/1.0',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    AUTH_TOKEN_PREFIX = 'token'

    def __init__(self, token: str, *, session: aiohttp.ClientSession = None):
        # Inicializa com autenticação e uma sessão opcional
        super().__init__(token, session=session)

    async def get_repo_info(self, owner: str, repo: str) -> dict:
        # Retorna as informações públicas de um repositório
        return await self.request(Router('GET', '/repos/{owner}/{repo}', owner=owner, repo=repo))

    async def get_commits(self, owner: str, repo: str, *, branch: str, per_page: int) -> list[dict]:
        # Retorna os commits de uma branch
        return await self.request(
            Router('GET', '/repos/{owner}/{repo}/commits', owner=owner, repo=repo),
            params={'sha': 'main', 'per_page': per_page}
        )


    async def get_file_content(self, owner: str, repo: str, file_path: str, branch: str = 'main') -> str:
        # Retorna o conteúdo *decodificado* de um arquivo de texto do repositório
        return await self.request(
            Router('GET', '/repos/{owner}/{repo}/contents/{file_path}', owner=owner, repo=repo, file_path=file_path),
            params={'ref': branch}
        )

    async def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        commit_message: str,
        content: str,
        sha: str,
        branch: str = 'main'
    ) -> dict:
        # Atualiza um arquivo existente usando o SHA e novo conteúdo
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        return await self.request(
            Router('PUT', '/repos/{owner}/{repo}/contents/{_path}', owner=owner, repo=repo, _path=path),
            json={
                'message': commit_message,
                'content': encoded_content,
                'sha': sha,
                'branch': branch
            }
        )

    async def get_branches(self, owner: str, repo: str) -> list[dict]:
        # Retorna a lista de todas as branches do repositório
        return await self.request(
            Router('GET', '/repos/{owner}/{repo}/branches', owner=owner, repo=repo)
        )

    async def get_branch(self, owner: str, repo: str, branch: str = 'main') -> dict:
        # Retorna os dados de uma branch específica
        return await self.request(
            Router('GET', '/repos/{owner}/{repo}/branches/{branch}', owner=owner, repo=repo, branch=branch)
        )

    async def list_directory(self, owner: str, repo: str, path: str, branch: str = 'main') -> list[dict]:
        # Lista o conteúdo (arquivos e pastas) de um diretório no repositório
        return await self.request(
            Router('GET', '/repos/{owner}/{repo}/contents/{_path}', owner=owner, repo=repo, _path=path),
            params={'ref': branch}
        )