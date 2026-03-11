from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.entity import Player
    from core.entity import Enemy


__version__ = "22.0"
__creation__ = "16-01-2026"


from typing import Protocol, runtime_checkable
from attr import dataclass
import random


from items.items import (generate_random_item, generate_random_resource, Item)
from items.resources import Resource


@runtime_checkable
class Loot(Protocol):
    def apply_to(self, player: Player) -> None:
        ...
    
    def describe(self) -> str:
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

    @staticmethod
    def give_loot(player: Player, loot_item):
        """
        Centralized function to give loot to player.
        Handles Item, Resource, gold (int), or resource tuples (resource_id, amount).
        
        Usage:
        - give_loot(player, item)  # Item instance
        - give_loot(player, ("iron_ore", 5))  # Resource with amount
        - give_loot(player, 100)  # Gold amount
        """
        if isinstance(loot_item, Loot):
            player.obtain(loot_item)
            return

        if isinstance(loot_item, Item):
            player.obtain(ItemLoot(loot_item))
            return

        if isinstance(loot_item, Resource):
            player.obtain(ResourceLoot(loot_item.type, 1))
            return

        if isinstance(loot_item, int):
            player.obtain(GoldLoot(loot_item))
            return

        if (
            isinstance(loot_item, tuple)
            and len(loot_item) == 2
            and isinstance(loot_item[0], str)
            and isinstance(loot_item[1], int)
        ):
            player.obtain(ResourceLoot(*loot_item))
            return

        raise TypeError(f"Unsupported loot type: {type(loot_item)}")



class ItemLoot:
    def __init__(self, item):
        self.item = item

    def apply_to(self, player: Player):
        player.inventory.append(self.item)
    
    def describe(self):
        raise NotImplementedError


class ResourceLoot:
    def __init__(self, resource_id: str, amount: int):
        self.resource_id = resource_id
        self.amount = amount

    def apply_to(self, player: Player):
        player.add_resource(self.resource_id, self.amount)

    def describe(self):
        raise NotImplementedError
    

class GoldLoot:
    def __init__(self, amount: int):
        self.amount = amount

    def apply_to(self, player: Player):
        player.gold += self.amount
        player.gold_collected += self.amount  # stats

    def describe(self):
        raise NotImplementedError
    
