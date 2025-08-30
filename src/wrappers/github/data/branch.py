from __future__ import annotations

from ..._base_dataclass import BaseDataClass

class GitHubBranchCommit(BaseDataClass):
    """
    Representa o commit vinculado a uma branch.

    Attributes:
        sha (str): SHA do commit.
        url (str): URL da API do commit.
    """

    sha: str
    url: str


class GitHubBranch(BaseDataClass):
    """
    Representa uma branch de um repositório no GitHub.

    Attributes:
        name (str): Nome da branch.
        commit (GitHubBranchCommit): Commit vinculado à branch.
        protected (bool): Indica se a branch está protegida.
    """
    name: str
    commit: GitHubBranchCommit
    protected: bool

    def __str__(self) -> str:
        return self.name