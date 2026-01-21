from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.entity import Player

__version__ = "6.0"
__creation__ = "16-01-2026"

from typing import Protocol

class Loot(Protocol):
    def apply_to(self, player: Player) -> None:
        ...



class ItemLoot:
    def __init__(self, item):
        self.item = item

    def apply_to(self, player: Player):
        player.inventory.append(self.item)


class ResourceLoot:
    def __init__(self, resource_id: str, amount: int):
        self.resource_id = resource_id
        self.amount = amount

    def apply_to(self, player: Player):
        player.add_resource(self.resource_id, self.amount)


class GoldLoot:
    def __init__(self, amount: int):
        self.amount = amount

    def apply_to(self, player: Player):
        player.gold += self.amount
        player.gold_collected += self.amount  # stats
