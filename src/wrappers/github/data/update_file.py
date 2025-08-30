from __future__ import annotations

from ..._base_dataclass import BaseDataClass, Field


class GitHubFileUpdateResponse(BaseDataClass):
    """
    Representa a resposta do GitHub após uma atualização de arquivo via API de conteúdo.
    """

    content: dict = Field(..., description="Informações do conteúdo atualizado")
    commit: dict = Field(..., description="Informações do commit realizado")
