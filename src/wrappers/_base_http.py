from __future__ import annotations

import logging
import aiohttp
from typing import Any, ClassVar, Literal, Optional, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from .file import File

_log = logging.getLogger(__name__)

__all__ = ('BaseRouter', 'BaseHTTPClient',)

class BaseRouter:
    """
    Classe responsável por construir URLs para requisições HTTP.

    Attributes:
        BASE (`ClassVar[str]`): URL base para as requisições.
    """
    BASE: ClassVar[str]

    def __init__(self, method: Literal['GET', 'POST', 'DELETE', 'PUT'], path: str, **parameters: Any):
        """
        Inicializa um objeto Router.

        Args:
            method (`Literal['GET', 'POST', 'DELETE', 'PUT']`): Método HTTP.
            path (`str`): Caminho relativo para a requisição.
            parameters (`any`): Parâmetros para formatar a URL.
        """
        self.method = method
        self.path = path
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url

class BaseHTTPClient:
    """
    Cliente HTTP assíncrono para realizar requisições.

    Attributes:
        DEFAULT_HEADERS (`ClassVar[dict]`): Cabeçalhos padrão para as requisições. **Default -> {}**.
        AUTH_HEADER_NAME (`ClassVar[str]`) : Nome do cabeçalho de autenticação. **Default -> 'Authorization'**.
        AUTH_TOKEN_PREFIX (`ClassVar[Optional[str]]`): Prefixo do token de autenticação. **Default -> None**.
    """
    DEFAULT_HEADERS: ClassVar[dict] = {}
    AUTH_HEADER_NAME: ClassVar[str] = 'Authorization'
    AUTH_TOKEN_PREFIX: ClassVar[Optional[str]] = None

    def __init__(self, token: Optional[str] = None, *, session: Optional[aiohttp.ClientSession] = None):
        """
        Inicializa o cliente HTTP.

        Args:
            token (`Optional[str]`): Token de autenticação.
            session (`Optional[aiohttp.ClientSession]`): Sessão HTTP opcional.
        """
        self.__session = session or None
        self.__token = token

    async def request(self, router: BaseRouter, **params: Any) -> Any:
        """
        Realiza uma requisição HTTP.

        Args:
            router (`BaseRouter`): Objeto Router contendo informações da requisição.
            params (`dict`): Argumentos adicionais para a requisição.

        Returns:
            Any: Resposta da requisição.
        
        Raises:
            aiohttp.ClientResponseError: Para erros HTTP com status >= 400.
        """
        if self.__session is None:
            self.__session = aiohttp.ClientSession()

        method, url = router.method, router.url
        headers = dict(self.DEFAULT_HEADERS)
        
        if self.__token is not None:
            if self.AUTH_TOKEN_PREFIX:
                headers[self.AUTH_HEADER_NAME] = f'{self.AUTH_TOKEN_PREFIX} {self.__token}'
            else:
                headers[self.AUTH_HEADER_NAME] = self.__token

        if 'file' in params:
            file: 'File' = params.pop('file')

            form = aiohttp.FormData()
            form.add_field('file', file.fp, filename=file.filename)
            params['data'] = form

        async with self.__session.request(method, url, headers=headers, **params) as resp:
            _log.debug(f'{method} {url} com {params} retornou status {resp.status}')
            status = resp.status
            content_type = resp.headers.get('Content-Type', '').lower()

            playload = await self._safe_parse_payload(resp, content_type)

            if status >= 400:
                _log.error(f'Erro {status} em {method} {url} - Payload: {playload}')

                if status == 401:
                    raise aiohttp.ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=resp.status,
                        message='Não autorizado. Verifique suas credenciais.',
                        headers=resp.headers,
                    )
                elif status == 403:
                    raise aiohttp.ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=resp.status,
                        message='Acesso proibido. Você não tem permissão para acessar este recurso.',
                        headers=resp.headers,
                    )
                elif status == 404:
                    raise aiohttp.ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=resp.status,
                        message='Recurso não encontrado. Verifique a URL.',
                        headers=resp.headers,
                    )
                elif status >= 500:
                    raise aiohttp.ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=resp.status,
                        message='Erro interno do servidor. Tente novamente mais tarde.',
                        headers=resp.headers,
                        )
                else:
                    raise aiohttp.ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=resp.status,
                        message=f'Erro {status} em {method} {url} - Payload: {playload}',
                        headers=resp.headers,
                    )

            return playload
            
    async def _safe_parse_payload(self, resp: aiohttp.ClientResponse, content_type: str) -> Any:
        """
        Analisa o payload da resposta de forma segura.

        Args:
            resp (`aiohttp.ClientResponse`): Resposta HTTP.
            content_type (`str`): Tipo de conteúdo da resposta.

        Returns:
            Any: Payload analisado.
        """
        if content_type.startswith('application/json'):
            return await resp.json()
        if content_type.startswith('text/') or content_type == 'application/xml':
            return await resp.text()
        return await resp.read()