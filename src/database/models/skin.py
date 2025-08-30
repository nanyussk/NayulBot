from __future__ import annotations

from pydantic import Field
from typing import Optional, Literal

from ._base import BaseDataClass

class ProfileSkin(BaseDataClass):
    """
    Representa uma skin de perfil.

    Attributes:
        id (`str`): ID único da skin.
        name (`str`): Nome da skin.
        price (`int`): Preço da skin em pérolas.
        rarity (`Literal[0, 1, 2, 3, 4]`): Raridade da skin.
        description (`Optional[str]`): Descrição da skin.
        author (`Optional[str]`): Autor da skin.
        url (`str`): URL da imagem da skin.
    """
    id: str = Field(alias='_id')
    name: str
    price: int
    rarity: Literal[0, 1, 2, 3, 4] = Field(ge=0, le=4)
    description: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    url: str

    def __str__(self) -> str:
        return f'{ProfileSkin.__name__}(id={self.id}, name={self.name}, rarity={self.rarity})'