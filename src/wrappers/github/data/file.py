from __future__ import annotations

import base64

from ..._base_dataclass import BaseDataClass, field_validator

class GitHubFile(BaseDataClass):
    """
    Representa um arquivo no repositório GitHub retornado pela API.

    Campos principais incluem informações básicas do arquivo e seu conteúdo,
    que é decodificado automaticamente se estiver em base64.
    """
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    content: str  # conteúdo em base64 vindo da API
    encoding: str

    @field_validator('content', mode='before')
    def decode_content(cls, v, info):
        """
        Validador que decodifica o conteúdo do arquivo de base64 para texto UTF-8
        se o encoding for base64.
        
        Args:
            v (str): conteúdo codificado em base64.
            values (dict): outros valores já validados no modelo.

        Returns:
            str: conteúdo decodificado em texto.
        """
        if info.data.get('encoding') == 'base64' and v is not None:
            return base64.b64decode(v).decode('utf-8')
        return v

    import base64

    def get_content(self) -> str:
        """Retorna o conteúdo decodificado do arquivo (caso esteja em base64)."""
        if self.encoding == 'base64' and self.content is not None:
            # O conteúdo pode ter que ser limpo de quebras de linha antes de decodificar
            cleaned = self.content.replace('\n', '')
            return base64.b64decode(cleaned).decode('utf-8')
        return self.content
