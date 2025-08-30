from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from ..._base_dataclass import BaseDataClass


class Owner(BaseDataClass):
    """
    Representa o proprietário de um repositório no GitHub.
    
    Attributes:
        login (str): Nome de usuário do proprietário.
        id (int): ID único do proprietário.
        avatar_url (str): URL do avatar do usuário.
        html_url (str): URL do perfil público do usuário.
        type (str): Tipo de conta (ex.: "User", "Organization").
        site_admin (bool): Indica se o usuário é administrador do GitHub.
    """
    login: str
    id: int
    avatar_url: str
    html_url: str
    type: str
    site_admin: bool

    def __str__(self) -> str:
        return self.login


class Permissions(BaseDataClass):
    """
    Representa as permissões do usuário no repositório.

    Attributes:
        admin (bool): Permissão de administrador.
        push (bool): Permissão para enviar alterações.
        pull (bool): Permissão para visualizar/clonar o repositório.
    """
    admin: bool
    push: bool
    pull: bool


class GitHubRepo(BaseDataClass):
    """
    Representa um repositório do GitHub com informações essenciais.

    Attributes:
        id (int): ID único do repositório.
        name (str): Nome curto do repositório.
        full_name (str): Nome completo (ex.: "usuario/repositorio").
        private (bool): Indica se o repositório é privado.
        owner (Owner): Proprietário do repositório.
        html_url (str): URL pública do repositório.
        description (Optional[str]): Descrição do repositório.
        fork (bool): Indica se é um fork de outro repositório.
        url (str): URL da API do repositório.

        created_at (datetime): Data de criação.
        updated_at (datetime): Data da última atualização.
        pushed_at (datetime): Data do último push.

        language (Optional[str]): Linguagem principal usada no repositório.
        stargazers_count (int): Número de estrelas recebidas.
        watchers_count (int): Número de usuários observando.
        forks_count (int): Número de forks.
        open_issues_count (int): Número de issues abertas.

        license (Optional[str]): Nome da licença, se houver.
        topics (List[str]): Tópicos (tags) associados ao repositório.
        visibility (str): Visibilidade (ex.: "public", "private").
        default_branch (str): Nome da branch padrão.
        permissions (Permissions): Permissões do usuário autenticado.
    """
    id: int
    name: str
    full_name: str
    private: bool
    owner: Owner
    html_url: str
    description: Optional[str]
    fork: bool
    url: str

    created_at: datetime
    updated_at: datetime
    pushed_at: datetime

    language: Optional[str]
    stargazers_count: int
    watchers_count: int
    forks_count: int
    open_issues_count: int

    license: Optional[str]
    topics: List[str]
    visibility: str
    default_branch: str
    permissions: Permissions

    def __str__(self) -> str:
        return f'{self.full_name} (private={self.private})'