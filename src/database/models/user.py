from __future__ import annotations

from datetime import datetime
from pydantic import Field
from typing import Optional, List

from ._base import BaseDataClass


class Profile(BaseDataClass):
    """
    Representa o perfil do usuário.

    Attributes:
        skin_now (`str`): Skin atual do usuário.
        skins (`List[str]`): Lista de skins desbloqueadas.
        about_me (`Optional[str]`): Descrição pessoal do usuário.
    """
    skin_now: str = Field(alias='skinNow', default='default')
    skins: List[str] = Field(default_factory=lambda: ['default'])
    about_me: Optional[str] = Field(alias='aboutMe', default=None)

class Cooldowns(BaseDataClass):
    """
    Gerencia os tempos de espera (cooldowns) do usuário.

    Attributes:
        daily (`Optional[datetime]`): Cooldown diário.
        reputation (`Optional[datetime]`): Cooldown de reputação.
        married (`Optional[datetime]`): Cooldown para se casar novamente após o divorcio.
        premium_expiration (`Optional[datetime]`): Data de expiração do status premium.
    """
    daily: Optional[datetime] = None
    reputation: Optional[datetime] = None
    married: Optional[datetime] = None
    premium_expiration: Optional[datetime] = Field(alias='premiumExpiration', default=None)

class MarriedStatus(BaseDataClass):
    """
    Representa as informações de casamento do usuário.

    Attributes:
        division_of_assets (`bool`): Indica se há divisão de bens no casamento.
        married_with (`int`): Id do usuário com quem está casado.
        since (`datetime`): Data do casamento.
        shared_pearls (`int`): Quantidade de pérolas compartilhadas.
    """
    division_of_assets: bool = Field(alias='divisionOfAssets')
    married_with: int = Field(alias='marriedWith')
    since: datetime
    shared_pearls: int = Field(alias='sharedPearls')

class BanStatus(BaseDataClass):
    """
    Representa as informações de banimento do usuário.

    Attributes:
        banned_by (`int`): Id do usuário que baniu o usuário.
        banned_at (`datetime`): Data do banimento.
        reason (`str`): Motivo do banimento.
    """
    banned_by: int = Field(alias='bannedBy')
    banned_at: datetime = Field(alias='bannedAt')
    reason: str = None

class UserData(BaseDataClass):
    """
    Modelo principal de dados do usuário.

    Attributes:
        id (`int`): Identificador único do usuário (mapeado de `_id` no MongoDB).
        pearls (`int`): Quantidade de pérolas do usuário.
        experience (`float`): Experiência do usuário.
        reputation (`int`): Reputação do usuário.
        accepted_terms (`bool`): Indica se os termos de uso foram aceitos.
        cai_uuid (`Optional[str]`): UUID do usuário.
        cooldowns (`Optional[Cooldowns]`): Cooldowns do usuário.
        married_status (`Optional[MarriedStatus]`): Informações de casamento do usuário.
        profile (`Optional[Profile]`): Perfil do usuário.
        ban (`Optional[BanStatus]`): Status de banimento do usuário.
    """
    id: int = Field(alias='_id')
    pearls: int = 0
    experience: float = 0.0
    reputation: int = 0
    accepted_terms: bool = Field(alias='acceptedTerms', default=False)
    cai_uuid: Optional[str] = Field(alias='caiUUID', default=None)
    profile: Optional[Profile] = Field(default_factory=Profile)
    cooldowns: Optional[Cooldowns] = Field(default_factory=Cooldowns)
    married_status: Optional[MarriedStatus] = Field(alias='marriedStatus', default=None)
    ban_status: Optional[BanStatus] = Field(alias='banStatus', default=None)

    def __str__(self) -> str:
        return f'{UserData.__name__}(id={self.id}, pearls={self.pearls}, accepted_terms={self.accepted_terms})'