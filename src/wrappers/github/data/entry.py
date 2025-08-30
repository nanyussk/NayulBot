from __future__ import annotations

from ..._base_dataclass import BaseDataClass
from typing import Optional

class GitHubEntry(BaseDataClass):
    """
    Representa uma entrada (arquivo ou diretório) no conteúdo de um repositório GitHub.
    
    Campos essenciais:
    - name: nome do arquivo ou diretório.
    - path: caminho completo dentro do repositório.
    - sha: hash do objeto.
    - type: 'file' ou 'dir'.
    - size: tamanho em bytes (0 para diretórios).
    - download_url: URL para baixar o arquivo (None para diretórios).
    """

    name: str
    path: str
    sha: str
    type: str
    size: int
    download_url: Optional[str] = None

    def __str__(self):
        return self.path
