from __future__ import annotations

from typing import TypedDict, Optional, List
from datetime import datetime
import discord

class PlayerStats(TypedDict):
    player: discord.Member
    start: datetime
    end: Optional[datetime]
    words_list: List[str]