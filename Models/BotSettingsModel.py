from dataclasses import dataclass


@dataclass
class BotSettings:
    refresh_time: float
    contact_name: str
    ValidationSettings: dict
