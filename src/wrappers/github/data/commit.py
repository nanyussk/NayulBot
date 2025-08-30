from pydantic import BaseModel
from typing import List, Optional


class CommitAuthor(BaseModel):
    """
    Informações do autor ou committer de um commit.

    Attributes:
        name (str): Nome do autor/committer.
        email (str): Email do autor/committer.
        date (str): Data e hora do commit (formato ISO 8601).
    """
    name: str
    email: str
    date: str


class CommitVerification(BaseModel):
    """
    Dados de verificação do commit.

    Attributes:
        verified (bool): Indica se o commit foi verificado.
        reason (str): Razão da verificação (ex: 'valid', 'unsigned').
    """
    verified: bool
    reason: str


class CommitDetails(BaseModel):
    """
    Detalhes do commit.

    Attributes:
        author (CommitAuthor): Informações do autor do commit.
        committer (CommitAuthor): Informações do committer.
        message (str): Mensagem do commit.
        comment_count (int): Número de comentários no commit.
        verification (CommitVerification): Informações sobre a verificação do commit.
    """
    author: CommitAuthor
    committer: CommitAuthor
    message: str
    comment_count: int
    verification: CommitVerification


class CommitParent(BaseModel):
    """
    Commit pai, usado para commits de merge.

    Attributes:
        sha (str): SHA do commit pai.
        url (str): URL da API para o commit pai.
    """
    sha: str
    url: str


class GitHubUser(BaseModel):
    """
    Dados básicos do usuário GitHub relacionado ao commit.

    Attributes:
        login (str): Nome de usuário do GitHub.
        id (int): ID numérico do usuário.
        avatar_url (str): URL do avatar do usuário.
        html_url (str): URL do perfil do usuário no GitHub.
    """
    login: str
    id: int
    avatar_url: str
    html_url: str


class GitHubCommit(BaseModel):
    """
    Representa um commit retornado pela API do GitHub.

    Attributes:
        sha (str): SHA do commit.
        commit (CommitDetails): Detalhes do commit.
        html_url (str): URL para visualização do commit no GitHub.
        author (Optional[GitHubUser]): Usuário autor do commit (pode ser None).
        committer (Optional[GitHubUser]): Usuário committer do commit (pode ser None).
        parents (List[CommitParent]): Lista dos commits pais.
    """
    sha: str
    commit: CommitDetails
    html_url: str
    author: Optional[GitHubUser]
    committer: Optional[GitHubUser]
    parents: List[CommitParent]