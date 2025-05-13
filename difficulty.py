__version__ = "50.0"
__creation__ = "08-05-2025"

import random

from data import EVENTS


class GameMode:
    def __init__(self, name="normal"):
        self.name = name
    
    def __str__(self):
        return self.name # str(self.difficulty) return "normal"

    def capitalize(self):
        return self.name.capitalize()  # Now we can call `self.difficulty.capitalize()` and not get an AttributeError

    def take_damage(self, player, damage):
        raise NotImplementedError

    def on_combat_start(self, player, enemy):
        """Hook called at the start of combat."""
        pass

    def on_item_use(self, player, item):
        """Hook called when player uses an item."""
        pass

    def has_inventory_limit(self):
        """Return True if this mode limits inventory size."""
        return False

    def get_inventory_limit(self):
        """Return the inventory limit if any."""
        return None

    def modify_damage_dealt(self, player, damage):
        """Modify damage dealt by player."""
        return damage

    def modify_damage_taken(self, player, damage):
        """Modify damage taken by player."""
        return damage

    def on_level_up(self, player):
        """Hook called when player levels up."""
        pass

    def get_room_count(self):
        # Valeur par défaut
        return random.randint(5, 8)

    def maybe_trigger_event(player):
        if random.random() < 0.2:  # 20% de chance
            event = random.choice(EVENTS)
            event.trigger(player)
    
    def get_available_rarities(self):
        return ["common", "uncommon", "rare", "epic", "legendary", "divine"]

    def get_rarity_boost(self):
        return 1.0

    def get_ng_plus(self, player):
        return player.ng_plus[self.name]
    
    def get_shop_item_num(self):
        return random.randint(5, 7)


class NormalMode(GameMode):
    def __init__(self):
        super().__init__("normal")

    def take_damage(self, player, damage):
        player.stats.hp = max(0, player.stats.hp - damage)
        return damage

    def modify_damage_dealt(self, player, damage):
        return damage

    def modify_damage_taken(self, player, damage):
        return damage

    def level_up_bonus(self):
        return {
            "hp": 10,
            "mana": 5,
            "stamina": 5,
            "attack": 2,
            "defense": 2,
            "agility": 1
        }
    
    def get_shop_item_num(self):
        return random.randint(5, 7)


class SoulsEnjoyerMode(GameMode):
    def __init__(self):
        super().__init__("soul_enjoyer")

    def take_damage(self, player, damage):
        # In Souls Enjoyer mode, damage is halved but player has less health
        true_damage = max(1, damage / 2)
        player.stats.permanent_stats["hp"] = max(0, player.stats.permanent_stats["hp"] - true_damage)
        player.stats.hp = player.stats.permanent_stats["hp"]
        return true_damage

    def modify_damage_dealt(self, player, damage):
        # Souls Enjoyer mode might increase player's damage output
        return int(damage * 1.2)

    def modify_damage_taken(self, player, damage):
        # Souls Enjoyer mode might reduce damage taken
        return int(damage * 0.8)

    def level_up_bonus(self):
        return {
            "hp": 10,
            "mana": 5,
            "stamina": 5,
            "attack": 2,
            "defense": 2,
            "agility": 1
        }

    def get_shop_item_num(self):
        return random.randint(3, 6)

class RealisticMode(GameMode):
    def __init__(self):
        super().__init__("realistic")

    def take_damage(self, player, damage):
        true_damage = max(1, damage / max(1, player.stats.defense))
        player.stats.permanent_stats["hp"] = max(0, player.stats.permanent_stats["hp"] - true_damage)
        player.stats.hp = player.stats.permanent_stats["hp"]
        return true_damage

    def has_inventory_limit(self):
        return True

    def get_inventory_limit(self):
        return 30  # Example

    def modify_damage_dealt(self, player, damage):
        # Realistic mode might reduce player's damage output due to realism
        return int(damage * 0.9)

    def modify_damage_taken(self, player, damage):
        # Realistic mode might increase damage taken due to harsher conditions
        return int(damage * 1.2)

    def level_up_bonus(self):
        return {
            "hp": 5,
            "mana": 3,
            "stamina": 3,
            "attack": 1,
            "defense": 1,
            "agility": 0
        }
    
    def get_room_count(self):
        return random.randint(50, 100)

    def get_available_rarities(self):
        return ["common", "uncommon", "rare", "epic", "legendary", "divine", "???"]

    def get_rarity_boost(self):
        return 1.0

    def get_shop_item_num(self):
        return random.randint(2, 5)