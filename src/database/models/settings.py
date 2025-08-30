from __future__ import annotations

from typing import List

from ._base import BaseDataClass, Field

class Settings(BaseDataClass):
    """
    Representa as configurações do bot.

    Args:
        staffs (`List[int]`): Lista de IDs dos staffs do bot.
    """
    _id: int = 0
    staffs: List[int] = Field(default_factory=list)