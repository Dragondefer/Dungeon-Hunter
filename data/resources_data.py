# Dungeon Hunter - (c) Dragondefer 2025
# Licensed under CC BY-NC 4.0

from enum import Enum, auto

class ResourceType(Enum):
    ORE = auto()
    PLANT = auto()
    MAGIC = auto()
    FOOD = auto()



resources_data_raw = {
    "iron_ore": {
        "name": "Iron Ore",
        "type": ResourceType.ORE,
        "rarity": "common",
        "description": "A basic metal used in forging.",
        "value": 5
    },
    "magic_essence": {
        "name": "Magic Essence",
        "rarity": "rare",
        "type": ResourceType.MAGIC,
        "description": "A glowing crystal full of arcane power.",
        "value": 50
    },
    "smithing_stone": {
        "name": "Smithing Stone",
        "rarity": "common",
        "type": ResourceType.ORE,
        "description": "A stone used to upgrade weapons.",
        "value": 10
    },
    "wood": {
        "name": "Wood",
        "rarity": "common",
        "type": ResourceType.PLANT,
        "description": "Basic wood used for crafting.",
        "value": 3
    }
}

