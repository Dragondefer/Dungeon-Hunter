from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.entity import Player
    from core.entity import Enemy


from attr import dataclass
from sympy import im


__version__ = "8.0"
__creation__ = "16-01-2026"

from typing import Protocol
import random


from items.items import (generate_random_item, generate_random_resource)


class Loot(Protocol):
    def apply_to(self, player: Player) -> None:
        ...


@dataclass
class LootContext:
    player: Player
    enemy: Enemy | None = None
    room_type: str | None = None
    level: int | None = None
    rarity_boost: float = 0.0
    


class LootFactory:

    @staticmethod
    def random_item(ctx: LootContext) -> ItemLoot:
        item = generate_random_item(
            player=ctx.player,
            enemy=ctx.enemy,
            rarity_boost=ctx.rarity_boost
        )
        return ItemLoot(item)

    @staticmethod
    def random_resource(ctx: LootContext) -> ResourceLoot:
        """
        Generate a random resource.
        """
        resource = generate_random_resource()
        return ResourceLoot(resource.type, amount=1)

    @staticmethod
    def treasure(ctx: LootContext) -> list[Loot]:
        """
        Generate loot for a treasure Room.
        """
        loot: list[Loot] = []

        loot.append(
            LootFactory.random_item(ctx)
            )

        if ctx.player.difficulty.allows_resources():
            loot.append(
                LootFactory.random_resource(ctx)
            )

        return loot



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
