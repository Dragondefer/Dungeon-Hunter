from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.entity import Player

__version__ = "795.0"
__creation__ = "09-03-2025"

# Dungeon Hunter - (c) DragonDeFer 2025
# Licensed under CC BY-NC 4.0

import random

from interface.colors import Colors
from engine.game_utility import clear_screen
from engine.logger import logger
from core.spells import Spell
from items.resources import Resource, generate_random_resource

debug = 0

#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ I̴̡̛ẗ̴̗́ë̵͕́m̴̛̠s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ h̵̤͒o̶͙͝l̷̫̈́ď̶̙ h̵̤͒i̴̊͜ď̶̙ď̶̙ë̵͕́n̸̻̈́ c̴̱͝ŭ̵͇r̷͍̈́s̸̱̅ë̵͕́s̸̱̅ ẗ̴̗́h̵̤͒ä̷̪́ẗ̴̗́ ď̶̙r̷͍̈́ä̷̪́i̴̊͜n̸̻̈́ ÿ̸̡́o̶͙͝ŭ̵͇r̷͍̈́ s̸̱̅o̶͙͝ŭ̵͇l̷̫̈́ s̸̱̅l̷̫̈́o̶͙͝ẅ̷̙́l̷̫̈́ÿ̸̡́.̵͇̆
class Item:
    """
    Represents any usable or equippable item in the game.

    Attributes:
        name (str): The name of the item.
        description (str): A brief description of the item.
        value (int): The in-game currency value of the item.

    Methods:
        __str__() -> str:
            Returns a formatted string representation of the item.
    """
    def __init__(self, name:str, description:str, value:int, rarity:str|None=None):
        self.name = name
        self.description = description
        self.value = value if value else 0
        self.rarity = rarity # Need to be adedd when generating items
    
    def __str__(self):
        return f"{self.name} - {self.description} (Value: {self.value} gold)"
    
    def to_dict(self):
        """Converts an item to a dictionary for saving."""
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "type": self.__class__.__name__,  # Sauvegarde le type d'objet
            "extra": self.__dict__  # Sauvegarde les attributs supplémentaires
        }

    @classmethod
    def from_dict(cls, data):
        """Crée un objet Item à partir d'un dictionnaire, en tenant compte du type spécifique."""
        item_type = globals().get(data["type"], Item)

        # Vérifier si 'extra' est bien défini pour éviter KeyError
        extras = data.get("extra", {})

        if item_type == Armor:
            # Extraction des valeurs spécifiques à l'armure
            defense = extras.get("effects", {}).get("defense", 0)
            armor_type = extras.get("armor_type", "generic")
            return Armor(data["name"], data["description"], data["value"], defense, armor_type)

        elif item_type == Weapon:
            # Récupérer directement `damage` depuis `extra`
            damage = extras.get("damage", 0)  
            return Weapon(data["name"], data["description"], data["value"], damage)

        elif item_type == Potion:
            # Gestion des potions
            effect_type = extras.get("effect_type", "heal")
            effect_value = extras.get("effect_value", 0)
            return Potion(data["name"], data["description"], data["value"], effect_type, effect_value)

        elif item_type in [Ring, Amulet, Belt]:
            # Gestion des anneaux / amulettes / belt (ajout d'effets)
            bonuses = extras.get("effects", extras.get("bonuses", {}))
            return item_type(data["name"], data["description"], data["value"], bonuses)

        elif item_type == Scroll:
            spell_data = extras.get("spell", {})
            spell = Spell.from_dict(spell_data)
            return Scroll(data["name"], data["description"], data["value"], spell)
    
        # Pour les autres types d'items (ex : consommables spéciaux)
        return item_type(data["name"], data["description"], data["value"], **extras)

    def apply_to(self, player: Player):
        player.inventory.append(self)

#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ G̵̨̽ë̵͕́ä̷̪́r̷͍̈́ m̴̛̠ä̷̪́ÿ̸̡́ b̸̼̅i̴̊͜n̸̻̈́ď̶̙ ÿ̸̡́o̶͙͝ŭ̵͇ ẗ̴̗́o̶͙͝ ä̷̪́ f̷̠͑ä̷̪́ẗ̴̗́ë̵͕́ ẅ̷̙́o̶͙͝r̷͍̈́s̸̱̅ë̵͕́ ẗ̴̗́h̵̤͒ä̷̪́n̸̻̈́ ď̶̙ë̵͕́ä̷̪́ẗ̴̗́h̵̤͒.̵͇̆
class Gear(Item):
    """
    Gère les objets équipables (armes, armures, anneaux, etc.).
    """
    def __init__(self, name, description, value, effects=None):
        super().__init__(name, description, value)
        self.effects = effects if effects else {}

    def __str__(self):
        effects_desc = ", ".join(f"{k}: +{v}" for k, v in self.effects.items())
        return f"{self.name} - {self.description} ({effects_desc}, Value: {self.value} gold)"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "type": self.__class__.__name__,
            "extra": {"effects": self.effects}
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruit un objet à partir d'un dictionnaire JSON."""
        item_type = globals().get(data["type"], Item)  # Trouve la classe correcte
        extras = data.get("extra", {})

        if item_type in [Ring, Amulet, Belt, Armor, Shield, Weapon]:
            effects = extras.get("effects", extras.get("bonuses", {}))
            return item_type(data["name"], data["description"], data["value"], effects)

        return item_type(data["name"], data["description"], data["value"], **extras)


#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ E̶͍̚q̴̨͝ŭ̵͇i̴̊͜p̵̦̆m̴̛̠ë̵͕́n̸̻̈́ẗ̴̗́ m̴̛̠ä̷̪́ÿ̸̡́ c̴̱͝ä̷̪́r̷͍̈́r̷͍̈́ÿ̸̡́ ẗ̴̗́h̵̤͒ë̵͕́ ẅ̷̙́h̵̤͒i̴̊͜s̸̱̅p̵̦̆ë̵͕́r̷͍̈́s̸̱̅ o̶͙͝f̷̠͑ f̷̠͑ä̷̪́l̷̫̈́l̷̫̈́ë̵͕́n̸̻̈́ h̵̤͒ë̵͕́r̷͍̈́o̶͙͝ë̵͕́s̸̱̅.̵͇̆
from .items import Gear

class Equipment:
    """Gère l'équipement du joueur (slots et bonus appliqués)."""
    def __init__(self, **kwargs):
        """Initialise les slots de l'équipement."""
        self.slots: dict[str, Gear|None] = {
            "main_hand": None,
            "off_hand": None,
            "helmet": None,
            "chest": None,
            "gauntlets": None,
            "leggings": None,
            "boots": None,
            "shield": None,
            "ring": None,
            "amulet": None,
            "belt": None
        }
        # Remplit les slots avec les équipements chargés
        for slot, item in kwargs.items():
            self.slots[slot] = item

    def to_dict(self):
        """Convertit l'équipement en dictionnaire pour la sauvegarde."""
        return {slot: item.to_dict() if item else None for slot, item in self.slots.items()}

    @classmethod
    def from_dict(cls, data):
        """Reconstruct Equipment object from dictionary."""
        eq = cls()
        for slot, item_data in data.items():
            if item_data is not None:
                from items.items import Item, Gear
                item = Item.from_dict(item_data)
                if isinstance(item, Gear):
                    eq.slots[slot] = item
                else:
                    eq.slots[slot] = None
            else:
                eq.slots[slot] = None
        return eq

    def __str__(self):
        """Affiche l'équipement sous forme lisible."""
        equipped_items = [f"{slot}: {item.name}" for slot, item in self.slots.items() if item]
        return ", ".join(equipped_items) if equipped_items else "No Equipment"
    
    def __getattr__(self, name):
        """Accès aux équipements via equipment.main_hand, etc."""
        if name in self.slots:
            item = self.slots[name]
            if isinstance(item, dict):  # Si c'est un dictionnaire, on le convertit en Gear
                self.slots[name] = Gear(**item)
            return self.slots[name]
        raise AttributeError(f"'Equipment' object has no attribute '{name}'")
    

    def equip(self, slot, item, player):
        """Équipe un objet dans le slot spécifié et applique ses effets."""
        global debug

        if slot not in self.slots:
            logger.warning(f"Invalid slot '{slot}' for {item.name} in equip()")
            print(f"{Colors.RED}ERROR: Invalid slot '{slot}' for {item.name}!{Colors.RESET}")
            return

        # Vérifie si un objet est déjà équipé et le déséquipe
        if self.slots[slot]:
            self.unequip(slot, player)

        # Équipe le nouvel objet
        self.slots[slot] = item
        logger.info(f"Equipping {item.name} in {slot}")
        print(f"\n{Colors.GREEN}Equipping{Colors.RESET} {item.name} {Colors.GREEN}in {slot}.{Colors.RESET}")
        if debug >= 1:
            print(f"DEBUG: Item info:\n{item}")


        # Met à jour les statistiques du joueur
        player.apply_all_equipment_effects(show_text=True)


    def unequip(self, slot, player):
        """Déséquipe un objet d'un slot."""
        if slot in self.slots and self.slots[slot]:
            removed_item = self.slots[slot]
            if removed_item:  # Check if there was an item to remove
                self.slots[slot] = None
                logger.info(f"Unequipped {removed_item.name} from {slot}")
                print(f"{Colors.YELLOW}Unequipped {removed_item.name} from {slot}.{Colors.RESET}")
                player.stats.update_total_stats()
                return removed_item
            return None
        logger.warning(f"No item equipped in {slot} to unequip()")
        print(f"{Colors.RED}No item equipped in {slot}.{Colors.RESET}")
        return None

    def get_equipped_items(self):
        """Retourne tous les objets actuellement équipés."""
        return {slot: item for slot, item in self.slots.items() if item}


class WeaponAttack:
    def __init__(self, name, power:float, cost:dict[str, int]={}, description="", status_effects=None, inertia=1.0):
        self.name = name              # nom de l'attaque
        self.power = power            # puissance relative (ex: x1.2)
        # cost can be a dict like {"stamina": 10, "hp": 5} or any other resource
        self.cost = cost
        self.description = description
        self.status_effects = status_effects or []  # list of status effects applied by this attack
        self.inertia = inertia # Affect the dodging chance (high inertia mean lower dodging chances)

    def __str__(self):
        cost_str = ", ".join(f"{k}: {v}" for k, v in self.cost.items()) if self.cost else "No cost"
        status_str = ", ".join(self.status_effects) if self.status_effects else "No status effects"
        return f"{self.name} (x{self.power}, cost: {cost_str}, status effects: {status_str})"


#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ W̸͕̆ë̵͕́ä̷̪́p̵̦̆o̶͙͝n̸̻̈́s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ ẗ̴̗́h̵̤͒i̴̊͜r̷͍̈́s̸̱̅ẗ̴̗́ f̷̠͑o̶͙͝r̷͍̈́ b̸̼̅l̷̫̈́o̶͙͝o̶͙͝ď̶̙ b̸̼̅ë̵͕́ÿ̸̡́o̶͙͝n̸̻̈́ď̶̙ ẗ̴̗́h̵̤͒ë̵͕́ ẅ̷̙́i̴̊͜ë̵͕́l̷̫̈́ď̶̙ë̵͕́r̷͍̈́'̸̱̅s̸̱̅ c̴̱͝o̶͙͝n̸̻̈́ẗ̴̗́r̷͍̈́o̶͙͝l̷̫̈́.̵͇̆
class Weapon(Gear):
    """
    Représente une arme équipable qui augmente les dégâts d'attaque.
    Hérite de Gear pour être compatible avec le système d'équipement.
    """
    def __init__(self, name, description, value, damage, attacks=None, upgrade_level=0):
        super().__init__(name, description, value, {"attack": damage})
        self.damage: int = damage
        # attacks is now a list of WeaponAttack instances
        self.attacks: list[WeaponAttack] = attacks or []  # List[WeaponAttack]
        self.upgrade_level: int = upgrade_level
        logger.debug(f"Weapon created: {self.name} with damage {self.damage} and special attacks {[str(a) for a in self.attacks]} at upgrade level {self.upgrade_level}")
    
    def __str__(self):
        attacks_str = ", ".join([attack.name for attack in self.attacks]) if self.attacks else "None"
        upgrade_str = f" +{self.upgrade_level}" if self.upgrade_level > 0 else ""
        return f"{self.name}{upgrade_str} - {self.description} (Damage: +{self.damage}, Special Attacks: {attacks_str}, Value: {self.value} gold)"
    
    def to_dict(self):
        """Convertit l'arme en dictionnaire pour la sauvegarde."""
        data = super().to_dict()
        data["extra"]["damage"] = self.damage
        data["extra"]["upgrade_level"] = self.upgrade_level
        # Save the attacks as list of dicts
        data["extra"]["attacks"] = [
            {
                "name": attack.name,
                "power": attack.power,
                "cost": attack.cost,
                "description": attack.description,
                "status_effects": attack.status_effects
            }
            for attack in self.attacks
        ]
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crée une arme à partir d'un dictionnaire sans modifier le format général."""
        extras = data.get("extra", {})
        attacks_data = extras.get("attacks", [])
        attacks = []
        for ad in attacks_data:
            attack = WeaponAttack(
                name=ad.get("name", ""),
                power=ad.get("power", 1),
                cost=ad.get("cost", {}),
                description=ad.get("description", ""),
                status_effects=ad.get("status_effects", [])
            )
            attacks.append(attack)
        return Weapon(
            data["name"],
            data["description"],
            data["value"],
            extras.get("damage", 0),
            attacks=attacks,
            upgrade_level=extras.get("upgrade_level", 0)
        )
    
    def get_mastery_key(self):
        return f"weapon::{self.__class__.__name__}"

    def upgrade(self, upgrade_data):
        """
        Upgrade the weapon based on upgrade_data dict containing:
        - 'damage_increase': int
        - 'new_name_suffix': str (e.g., '+1')
        """
        self.damage += upgrade_data.get("damage_increase", 0)
        self.upgrade_level += 1
        suffix = upgrade_data.get("new_name_suffix", f"+{self.upgrade_level}")
        if suffix not in self.name:
            self.name = f"{self.name} {suffix}"

    def get_upgrade_level(self):
        return self.upgrade_level

# New weapon subclasses with class bonuses
class Sword(Weapon):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value, damage)

    def get_class_bonus(self):
        # Bonus for Knight class
        return {"max_hp": 20, "defense": 5}

class Bow(Weapon):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value, damage)

    def get_class_bonus(self):
        # Bonus for Archer class
        return {"attack": 10, "agility": 5}

class Staff(Weapon):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value, damage)

    def get_class_bonus(self):
        # Bonus for Mage class
        return {"magic_damage": 15, "mana": 20}



#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ A̷̛͠r̷͍̈́m̴̛̠o̶͙͝r̷͍̈́ m̴̛̠ä̷̪́ÿ̸̡́ ẗ̴̗́r̷͍̈́ä̷̪́p̵̦̆ ẗ̴̗́h̵̤͒ë̵͕́ ẅ̷̙́ë̵͕́ä̷̪́r̷͍̈́ë̵͕́r̷͍̈́ i̴̊͜n̸̻̈́ ë̵͕́ẗ̴̗́ë̵͕́r̷͍̈́n̸̻̈́ä̷̪́l̷̫̈́ ẗ̴̗́o̶͙͝r̷͍̈́m̴̛̠ë̵͕́n̸̻̈́ẗ̴̗́.̵͇̆
class Armor(Gear):
    """Represents an equippable armor piece that enhances defense."""
    def __init__(self, name, description, value, defense, armor_type=None):
        super().__init__(name, description, value, {"defense": defense})
        self.defense = defense
        self.armor_type = armor_type  # "helmet", "chestplate", "leggings", etc.
        logger.debug(f"Armor created: {self.name} with defense {defense}")

    def to_dict(self):
        data = super().to_dict()
        data["extra"]["armor_type"] = self.armor_type
        return data


#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ S̶̤̕h̵̤͒i̴̊͜ë̵͕́l̷̫̈́ď̶̙s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ b̸̼̅l̷̫̈́o̶͙͝c̴̱͝k̵̢͝ m̴̛̠o̶͙͝r̷͍̈́ë̵͕́ ẗ̴̗́h̵̤͒ä̷̪́n̸̻̈́ j̶̩̈́ŭ̵͇s̸̱̅ẗ̴̗́ ä̷̪́ẗ̴̗́ẗ̴̗́ä̷̪́c̴̱͝k̵̢͝s̸̱̅.̵͇̆
class Shield(Gear):
    """Represents an equippable shield that provides high defense and blocking."""
    def __init__(self, name, description, value, defense, block_chance):
        super().__init__(name, description, value, {"defense": defense})
        self.block_chance = block_chance  # Chance de bloquer une attaque (ex: 20%)
        logger.debug(f"Shield created: {self.name} with block chance {block_chance}")

    def to_dict(self):
        data = super().to_dict()
        data["extra"]["block_chance"] = self.block_chance
        return data


#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ G̵̨̽ä̷̪́ŭ̵͇n̸̻̈́ẗ̴̗́l̷̫̈́ë̵͕́ẗ̴̗́s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ b̸̼̅i̴̊͜n̸̻̈́ď̶̙ ẗ̴̗́h̵̤͒ë̵͕́ ẅ̷̙́ë̵͕́ä̷̪́r̷͍̈́ë̵͕́r̷͍̈́'̸̱̅s̸̱̅ s̸̱̅o̶͙͝ŭ̵͇l̷̫̈́ ẗ̴̗́o̶͙͝ ď̶̙ä̷̪́r̷͍̈́k̵̢͝ f̷̠͑o̶͙͝r̷͍̈́c̴̱͝ë̵͕́s̸̱̅.̵͇̆
class Gauntlets(Gear):
    """Represents an equippable gauntlet that increases strength and defense."""
    def __init__(self, name, description, value, defense, strength_boost, effect=None):
        super().__init__(name, description, value, {"defense": defense, "strength": strength_boost})
        logger.debug(f"Gauntlets created: {self.name} with defense {defense} and strength boost {strength_boost}")
        self.defense = defense
        self.strength_boost = strength_boost
        self.effects = effect if effect else {}


    def apply_effect(self, player):
        """Applique les effets des gants au joueur."""
        for stat, bonus in self.effects.items():
            player.stats.__dict__[stat] += bonus
    
    def __str__(self):
        return f"{self.name} - {self.description} (Defense: +{self.defense}, Effects: {self.effects}, Value: {self.value} gold)"

    def to_dict(self):
        return super().to_dict()


#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ A̷̛͠m̴̛̠ŭ̵͇l̷̫̈́ë̵͕́ẗ̴̗́s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ ẅ̷̙́h̵̤͒i̴̊͜s̸̱̅p̵̦̆ë̵͕́r̷͍̈́ s̸̱̅ë̵͕́c̴̱͝r̷͍̈́ë̵͕́ẗ̴̗́s̸̱̅ o̶͙͝f̷̠͑ f̷̠͑o̶͙͝r̷͍̈́g̸̻̿o̶͙͝ẗ̴̗́ẗ̴̗́ë̵͕́n̸̻̈́ r̷͍̈́ë̵͕́ä̷̪́l̷̫̈́m̴̛̠s̸̱̅.̵͇̆
class Amulet(Gear):
    """Represents an equippable amulet with magical bonuses."""
    def __init__(self, name, description, value, effects):
        super().__init__(name, description, value, effects)
        logger.debug(f"Amulet created: {self.name} with effects {effects}")

#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ R̷̞͝i̴̊͜n̸̻̈́g̸̻̿s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ c̴̱͝ä̷̪́r̷͍̈́r̷͍̈́ÿ̸̡́ c̴̱͝ŭ̵͇r̷͍̈́s̸̱̅ë̵͕́s̸̱̅ ẗ̴̗́h̵̤͒ä̷̪́ẗ̴̗́ ẗ̴̗́ẅ̷̙́i̴̊͜s̸̱̅ẗ̴̗́ f̷̠͑ä̷̪́ẗ̴̗́ë̵͕́.̵͇̆
class Ring(Gear):
    """Represents an equippable ring that grants magical or stat bonuses."""
    def __init__(self, name, description, value, effects):
        super().__init__(name, description, value, effects)
        logger.debug(f"Ring created: {self.name} with effects {effects}")

#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ B̵̕͜ë̵͕́l̷̫̈́ẗ̴̗́s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ ẗ̴̗́i̴̊͜g̸̻̿h̵̤͒ẗ̴̗́ë̵͕́n̸̻̈́ ẅ̷̙́i̴̊͜ẗ̴̗́h̵̤͒ ä̷̪́ ẅ̷̙́i̴̊͜l̷̫̈́l̷̫̈́ o̶͙͝f̷̠͑ ẗ̴̗́h̵̤͒ë̵͕́i̴̊͜r̷͍̈́ o̶͙͝ẅ̷̙́n̸̻̈́.̵͇̆
class Belt(Gear):
    """Represents an equippable belt that boosts stamina or defense."""
    def __init__(self, name, description, value, effects):
        super().__init__(name, description, value, effects)
        logger.debug(f"Belt created: {self.name} with effects {effects}")



#̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ P̶̺̒o̶͙͝ẗ̴̗́i̴̊͜o̶͙͝n̸̻̈́s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ h̵̤͒ä̷̪́v̶̼͝ë̵͕́ s̸̱̅i̴̊͜ď̶̙ë̵͕́ ë̵͕́f̷̠͑f̷̠͑ë̵͕́c̴̱͝ẗ̴̗́s̸̱̅ b̸̼̅ë̵͕́ÿ̸̡́o̶͙͝n̸̻̈́ď̶̙ h̵̤͒ë̵͕́ä̷̪́l̷̫̈́i̴̊͜n̸̻̈́g̸̻̿.̵͇̆
class Potion(Item):
    """
    Represents a consumable potion with temporary effects.

    Inherits from:
        Item (Base class for all items)

    Attributes:
        effect_type (str): The type of effect (e.g., "heal", "attack_boost").
        effect_value (int): The numerical effect applied to the player.

    Methods:
        use(player: Player) -> None:
            Applies the potion's effect to the player and removes it from inventory.
    """
    def __init__(self, name, description, value, effect_type, effect_value):
        super().__init__(name, description, value)
        self.effect_type = effect_type  # "heal", "attack_boost", "defense_boost", etc.
        self.effect_value = effect_value
    
    def use(self, player):
        global debug

        from core.status_effects import EFFECT_MAP

        # Map potion effect_type strings to status effect class names in EFFECT_MAP
        effect_class_name_map = {
            "heal": "Healing",
            "attack_boost": "Attack Boost",
            "defense_boost": "Defense Boost",
            "luck_boost": "Luck Boost",
            "fire_resistance": "Fire Resistance"
        }

        effect_class_name = effect_class_name_map.get(self.effect_type)

        if effect_class_name is None:
            logger.warning(f"Unknown potion effect type: {self.effect_type}")
            print(f"{Colors.RED}The {self.name} has an unknown effect and does nothing.{Colors.RESET}")
        else:
            effect_class = EFFECT_MAP.get(effect_class_name)
            if effect_class_name == "Healing":
                # Healing effect is immediate, no duration
                if effect_class:
                    effect = effect_class(self.effect_value)
                    effect.apply(player)
                else:
                    # Fallback healing logic if effect class not found
                    player.heal(self.effect_value)
                logger.info(f"Player used a healing potion: {self.name}")
                print(f"{Colors.GREEN}You drink the {self.name} and recover {self.effect_value} HP!{Colors.RESET}")
            else:
                # For other effects, create with duration = effect_value
                if effect_class:
                    effect = effect_class(duration=self.effect_value)
                    effect.apply(player)
                else:
                    print(f"{Colors.RED}Effect type {effect_class_name} not found in EFFECT_MAP!{Colors.RESET}")
                logger.info(f"Player used a {self.effect_type} potion: {self.name}")
                print(f"{Colors.CYAN}You drink the {self.name} and gain {self.effect_type.replace('_', ' ')} for {self.effect_value} turns!{Colors.RESET}")

        # Remove from inventory after use
        try:
            player.inventory.remove(self)
        except ValueError as e:
            logger.warning(f"Failed to remove potion from inventory: {e}")
            pass

    def __str__(self):
        effect_desc = ""
        if self.effect_type == "heal":
            effect_desc = f"Heals {self.effect_value} HP"
        elif self.effect_type == "attack_boost":
            effect_desc = f"Attack +{self.effect_value}"
        elif self.effect_type == "defense_boost":
            effect_desc = f"Defense +{self.effect_value}"
        elif self.effect_type == "luck_boost":
            effect_desc = f"Luck +{self.effect_value}"
        
        return f"{self.name} - {self.description} ({effect_desc}, Value: {self.value} gold)"
    
    def to_dict(self):
        """Converts a potion to a dictionary for saving."""
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "type": self.__class__.__name__,
            "extra": {
                "effect_type": self.effect_type,
                "effect_value": self.effect_value
            }
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an item from a dictionary."""
        item_type = globals().get(data["type"], Item)

        if item_type == Potion:
            item = item_type(
                data["name"], 
                data["description"], 
                data["value"], 
                data["extra"]["effect_type"], 
                data["extra"]["effect_value"]
            )
        else:
            item = item_type(data["name"], data["description"], data["value"])

        item.__dict__.update(data["extra"])  # Restaure les attributs supplémentaires
        return item


potion_list = (
    Potion("Small Health Potion", "A tiny vial of red liquid", 10, "heal", 20)
)    

# ̶̼͝ B̵̕͜ë̵͕́ẅ̷̙́ä̷̪́r̷͍̈́ë̵͕́:̴̨͝ S̷̛͠c̷͍̈́r̶̛̠o̴̊͜l̷̫̈́l̵͇̆s̸̱̅ m̴̛̠ä̷̪́ÿ̸̡́ c̴̱͝o̶͙͝n̷͍̈́ẗ̷͍́ả̸̭i̴̊͜n̸̻̈́ s̸̱̅p̵̆ͦě̶́ľ̶́ḽ̷̈́ŝ̸̭ o̴̊͜f̵͇̆ f̷̠͑o̶͙͝r̷͍̈́ĝ̸̭o̶͙͝ṱ̴̈́ť̴́ě̵́ṋ̸̉ p̴̊͜ǒ̶́w̶̌́ḙ̸̉r̵͇̆.̵͇̆
class Scroll(Item):
    """
    Represents a consumable scroll that casts a spell when used.

    Attributes:
        name (str): The name of the scroll.
        description (str): Description of the scroll.
        value (int): The value of the scroll.
        spell (Spell): The spell contained in the scroll.
    """
    def __init__(self, name, description, value, spell, rarity=None):
        super().__init__(name, description, value, rarity)
        self.spell = spell

    def __str__(self):
        return f"{self.name} (Scroll) - {self.description}"
    
    def to_dict(self):
        """Convertit le scroll en dictionnaire compatible avec Item."""
        data = {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "type": self.__class__.__name__,
            "extra": {
                "spell": self.spell.to_dict()
            }
        }
        return data
    

    @classmethod
    def from_dict(cls, data):
        extras = data.get("extra", {})
        spell_data = extras.get("spell", {})
        spell = Spell.from_dict(spell_data)

        return cls(
            data["name"],
            data["description"],
            data["value"],
            spell,
            rarity=extras.get("rarity", None)
        )


    def use(self, caster, target):
        """
        Use the scroll to cast its spell and consume the scroll.

        Args:
            caster (Player): The entity using the scroll.
            target (Entity): The target of the spell.
        """
        success = self.spell.cast(caster, target)
        if success:
            try:
                caster.inventory.remove(self)
                print(f"{Colors.YELLOW}The scroll of {self.spell.name} crumbles to dust after use.{Colors.RESET}")
            except ValueError:
                logger.warning(f"Scroll {self.name} not found in inventory during use.")
        return success


# D​un​g​e​o​n​ ​Hu​n​te​r​ ​-​ ​(c​)​ ​D​r​ag​on​de​fe​r​ ​2​02​5
# L​i​ce​n​s​e​d​ u​n​d​er​ ​C​C​-B​Y​-​N​C ​4​.​0


def random_combat_description():
    return random.choice([
    "a dimly lit chamber with strange markings on the walls",
    "a spacious cavern with stalactites hanging from the ceiling",
    "an ancient hall with crumbling pillars",
    "a damp room with the smell of decay",
    "a chamber filled with old weapons and armor"
])
def random_treasure_description():
    return random.choice([
    "a small treasure room with a broken chest",
    "an ornate chamber with gilded decorations",
    "a hidden alcove with a small lockbox",
    "a vault with scattered coins and gems",
    "a forgotten storeroom with dusty shelves"
])
def random_trap():
    return {
    "type": "damage",
    "description": random.choice([
    "Spikes shoot up from the floor!",
    "A poisoned dart flies out from the wall!",
    "The floor gives way beneath you!"
]),
    "value": random.randint(5, 15),
    "triggered": False
}

def random_rest_description():
    return random.choice([
    "a quiet sanctuary with a small campfire",
    "a peaceful chamber with a spring of fresh water",
    "a secluded room with comfortable bedding",
    "a warm room with the remains of an old campsite"
])

def get_available_rarities(player, difficulty, level, rarity=None):
    """Determine available rarities based on player difficulty and level."""
    rarities_ls = ["common", "uncommon", "rare", "epic", "legendary", "divine", "???"]
    available_rarities = difficulty.get_available_rarities()
    
    # Adapt rarities to player level (level 1 max: rare, level 2: max = epic...)
    if level <= len(available_rarities) and not rarity:  
        available_rarities = available_rarities[:level + 2]
    
    return available_rarities

def calculate_rarity(available_rarities, rarity_boost, rarity=None):
    """Calculate item rarity based on available rarities and boost factor."""
    if rarity:
        return rarity
        
    # Adjust rarity weights based on rarity_boost
    rarity_weights = {
        "common": 0.485 / rarity_boost,
        "uncommon": 0.2 / rarity_boost,
        "rare": 0.15 * rarity_boost,
        "epic": 0.1 * rarity_boost,
        "legendary": 0.05 * rarity_boost,
        "divine": 0.01 * rarity_boost,
        "???": 0.005,
    }

    # Normalize probabilities to sum to 1
    total_weight = sum(rarity_weights.values())
    normalized_weights = {key: value / total_weight for key, value in rarity_weights.items()}

    # Filter available rarities that exist in normalized weights
    valid_rarities = [r for r in available_rarities if r in normalized_weights]

    # Check if valid rarities list is not empty
    if not valid_rarities:
        return "common"
    
    # Select a rarity with adjusted probabilities
    return random.choices(
        valid_rarities, 
        weights=[normalized_weights[r] for r in valid_rarities]
    )[0]

def get_rarity_data():
    """Return multipliers and color coding for each rarity."""
    multipliers = {
        "common": 1,
        "uncommon": 1.5,
        "rare": 2,
        "epic": 3,
        "legendary": 5,
        "divine": 10,
        "???": 100
    }
    
    colors = {
        "common": Colors.WHITE,
        "uncommon": Colors.GREEN,
        "rare": Colors.BLUE,
        "epic": Colors.MAGENTA,
        "legendary": Colors.YELLOW,
        "divine": Colors.rainbow_text,
        "???": lambda text: Colors.gradient_text(text, (0, 0, 0), (255, 0, 0))
    }
    
    prefixes = {
        "common": ["Common", "Basic", "Standard", "Ordinary", "Usual", "Normal"],
        "uncommon": ["Uncommon", "Sharp", "Sturdy", "Reliable", "Balanced"],
        "rare": ["Rare", "Advanced", "Superior"],
        "epic": ["Epic", "Exceptional", "Impressive", "Masterwork"],
        "legendary": ["Legendary", "Ancient", "Mythical", "Enchanted"],
        "divine": ["Divine", "Holy", "Sacred", "Blessed", "Miraculous", "Supernatural", "Celestial"],
        "???": ["Unknown"]
    }
    
    return {
        "multipliers": multipliers,
        "colors": colors,
        "prefixes": prefixes
    }

def get_enemy_set_info(enemy_type):
    """Get armor and weapon set info for a specific enemy type."""
    from data import enemy_sets
    if enemy_type and enemy_type in enemy_sets:
        set_type = enemy_sets[enemy_type]
        return {
            "armor": set_type.get("armor", ""),
            "weapon": set_type.get("weapon", "")
        }
    return {"armor": "", "weapon": ""}

# Add a dictionary mapping weapon types to default WeaponAttack instances
default_weapon_attacks = {
    "Sword": [
        WeaponAttack(name="Slash", power=1.2, cost={"stamina": 10}, description="A quick slash attack."),
        WeaponAttack(name="Heavy Strike", power=1.5, cost={"stamina": 20}, description="A powerful heavy strike.", status_effects=["stun"])
    ],
    "Axe": [
        WeaponAttack(name="Chop", power=1.3, cost={"stamina": 15}, description="A strong chopping attack."),
        WeaponAttack(name="Cleave", power=1.6, cost={"stamina": 25}, description="A wide cleave attack hitting multiple enemies.")
    ],
    "Dagger": [
        WeaponAttack(name="Stab", power=1.1, cost={"stamina": 8}, description="A quick stabbing attack."),
        WeaponAttack(name="Poisoned Blade", power=1.2, cost={"stamina": 12}, description="A stab with poison effect.", status_effects=["poison"])
    ],
    "Mace": [
        WeaponAttack(name="Smash", power=1.4, cost={"stamina": 18}, description="A heavy smashing attack."),
        WeaponAttack(name="Crush", power=1.7, cost={"stamina": 30}, description="A crushing blow that can stun.", status_effects=["stun"])
    ],
    "Staff": [
        WeaponAttack(name="Magic Bolt", power=1.3, cost={"mana": 15}, description="A bolt of magical energy."),
        WeaponAttack(name="Arcane Blast", power=1.8, cost={"mana": 30}, description="A powerful arcane explosion.", status_effects=["mana_boost"])
    ],
    "Bow": [
        WeaponAttack(name="Arrow Shot", power=1.2, cost={"stamina": 10}, description="A precise arrow shot."),
        WeaponAttack(name="Power Shot", power=1.6, cost={"stamina": 20}, description="A powerful shot that pierces armor.")
    ]
}

def create_weapon(level, rarity, prefix, weapon_type, value_base, rarity_data, special_attacks=None):
    """Create a weapon item."""
    multipliers = rarity_data["multipliers"]
    colors = rarity_data["colors"]
    
    damage = int((1 + level) * multipliers[rarity])
    name = f"{prefix} {weapon_type}"
    
    # Find rarity corresponding to prefix
    rarity_prefixes = rarity_data["prefixes"]
    rarity_key = next((key for key, values in rarity_prefixes.items() if prefix in values), rarity)
    
    # Apply correct color based on found rarity
    colored_name = colors[rarity_key](name) if callable(colors[rarity_key]) else f"{colors[rarity_key]}{name}{Colors.RESET}"
    
    desc = f"A level {level} {prefix} weapon"
    
    # Use default attacks for weapon_type if special_attacks not provided
    attacks = []
    if special_attacks:
        for attack_name, attack_func in special_attacks:
            # Create WeaponAttack with default cost and description
            attacks.append(WeaponAttack(name=attack_name, power=1.0, cost={}, description="Special attack", status_effects=[]))
    else:
        attacks = default_weapon_attacks.get(weapon_type, [])
    
    return Weapon(colored_name, desc, value_base, damage, attacks=attacks)

def create_armor(level, rarity, prefix, armor_type, value_base, rarity_data, armor_set_type=""):
    """Create an armor item."""
    multipliers = rarity_data["multipliers"]
    colors = rarity_data["colors"]
    
    if armor_set_type:
        name_prefix = f"{prefix} {armor_set_type}"
    else:
        name_prefix = f"{prefix}"
        
    defense = int((2 + level) * multipliers[rarity])
    name = f"{name_prefix} {armor_type}"
    
    colored_name = colors[rarity](name) if callable(colors[rarity]) else f"{colors[rarity]}{name}{Colors.RESET}"
    desc = f"A level {level} {prefix} armor piece"
    
    return Armor(colored_name, desc, value_base, defense, armor_type)

def create_accessory(level, rarity, prefix, item_type, value_base, rarity_data):
    """Create a ring, amulet, or belt item."""
    multipliers = rarity_data["multipliers"]
    colors = rarity_data["colors"]
    
    if item_type == "ring":
        effect = {"luck": int((1 + (level // 2)) * multipliers[rarity])}
        name = f"{prefix} Ring"
        desc = "A magical ring that enhances luck"
        colored_name = colors[rarity](name) if callable(colors[rarity]) else f"{colors[rarity]}{name}{Colors.RESET}"
        return Ring(colored_name, desc, value_base, effect)
        
    elif item_type == "amulet":
        effect = {"defense": int((1 + (level // 2)) * multipliers[rarity])}
        name = f"{prefix} Amulet"
        desc = "A mystical amulet that grants protection"
        colored_name = colors[rarity](name) if callable(colors[rarity]) else f"{colors[rarity]}{name}{Colors.RESET}"
        return Amulet(colored_name, desc, value_base, effect)
        
    elif item_type == "belt":
        effect = {"agility": int((1 + (level // 2)) * multipliers[rarity])}
        name = f"{prefix} Belt"
        desc = "A sturdy belt that enhances movement speed"
        colored_name = colors[rarity](name) if callable(colors[rarity]) else f"{colors[rarity]}{name}{Colors.RESET}"
        return Belt(colored_name, desc, value_base, effect)

# D‌u​n‍g​e​o​n​ ‌H​u​n‌t‍e​r​ ‌-​ ‌(c)‌ ‌D​rag‍o​n​d‌e‍f​e‍r ​2‍02​5
# L‍i‍c​en​s​e‍d​ ‌u‌n‍d‍e‌r‌ ‌C​C-​BY-​N​C ​4​.0

def create_potion(level, rarity, prefix, item_name, value_base, rarity_data):
    """Create a potion item."""
    multipliers = rarity_data["multipliers"]
    colors = rarity_data["colors"]
    
    potion_types = {
        "Healing Potion":         {"effect_type": "heal",          "effect_value": int(20 * level * multipliers[rarity])},
        "Strength Elixir":        {"effect_type": "attack_boost",  "effect_value": int(2 * multipliers[rarity])},
        "Iron Skin Tonic":        {"effect_type": "defense_boost", "effect_value": int(2 * multipliers[rarity])},
        "Lucky Charm Brew":       {"effect_type": "luck_boost",    "effect_value": int(1 * multipliers[rarity])},
        "Healing Spring Potion":  {"effect_type": "heal",          "effect_value": int(10 * multipliers[rarity])},
        "Dragon's Breath Potion": {"effect_type": "fire_resistance",   "effect_value": int(2 * multipliers[rarity])}
    }
    
    potion_name = item_name if item_name in potion_types else random.choice(list(potion_types.keys()))
    potion = potion_types[potion_name]
    
    name = f"{prefix} {potion_name}"
    colored_name = colors[rarity](name) if callable(colors[rarity]) else f"{colors[rarity]}{name}{Colors.RESET}"
    
    effect_desc = {
        "heal": f"Restores {potion['effect_value']} HP",
        "attack_boost": f"Increases Attack by {potion['effect_value']}",
        "defense_boost": f"Increases Defense by {potion['effect_value']}",
        "luck_boost": f"Increases Luck by {potion['effect_value']}",
        "fire_resistance": f"Grants fire resistance for {potion['effect_value']} turns"
    }.get(potion["effect_type"], "")
    
    return Potion(colored_name, effect_desc, value_base, potion["effect_type"], potion["effect_value"])


def generate_random_resource_item(resource_type=None):
    """
    Generate a random resource item.
    
    Args:
        resource_type (ResourceType | None): Specific resource type to generate, or None for any type.
    
    Returns:
        Resource: A randomly generated resource object.
    """
    return generate_random_resource(resource_type)


def generate_items_and_resources(player: Player, include_resources: bool = False, num_items: int = 1, num_resources: int = 1, **kwargs):
    """
    Generate multiple items and optionally resources at once.
    
    Args:
        player (Player): The player instance.
        include_resources (bool): Whether to include resources in the generation. Default False.
        num_items (int): Number of items to generate. Default 1.
        num_resources (int): Number of resources to generate (only if include_resources=True). Default 1.
        **kwargs: Additional arguments to pass to generate_random_item.
    
    Returns:
        list: A list of generated items and resources.
    """
    result = []
    
    # Generate items
    for _ in range(num_items):
        result.append(generate_random_item(player=player, **kwargs))
    
    # Generate resources if requested
    if include_resources:
        for _ in range(num_resources):
            result.append(generate_random_resource_item())
    
    return result


def generate_random_item(player:Player, enemy=None, item_type=None, rarity=None, item_name=None, rarity_boost=None, available_rarities=None, level_boost=0, enemy_type=None):
    """Generate a specific or random item with customizable attributes."""
    global debug
    debug = 0

    level = (player.dungeon_level + level_boost)
    difficulty = player.difficulty
    
    # Determine enemy type
    if not enemy_type and enemy:
        enemy_type = enemy.type
    
    # Get difficulty-specific rarity boost if not provided
    if rarity_boost is None or rarity_boost <= 0:
        rarity_boost = difficulty.get_rarity_boost()

    # D​un​g​e​o​n​ ​Hu​n​t​e​r​ ​-​ ​(​c​)​ ​D​r​ag​o​nd​ef​e​r​ ​2​0​2​5
    # Determine available rarities based on player and difficulty
    if available_rarities is None:
        available_rarities = get_available_rarities(player, difficulty, level, rarity)

    # Calculate item rarity
    rarity = calculate_rarity(available_rarities, rarity_boost, rarity)
    
    # Get rarity-related data (multipliers, colors, prefixes)
    rarity_data = get_rarity_data()
    
    # L​i​ce​n​s​e​d​ u​n​de​r​ ​C​C-​B​Y​-N​C​ ​4​.​0
    # Get a random prefix based on rarity
    prefix = random.choice(rarity_data["prefixes"].get(rarity, [""]))
    
    # Get enemy-specific set info
    enemy_set_info = get_enemy_set_info(enemy_type)
    armor_set_type = enemy_set_info["armor"]
    weapon_set_type = enemy_set_info["weapon"]
    
    # Determine item type if not specified
    if enemy_type:
        item_type = random.choice(["armor", "weapon"])
    elif item_type is None:
        item_type = random.choice(["weapon", "armor", "potion", "ring", "amulet", "belt"])
    
    # Base value scaling with level and rarity
    value_base = int(50 * level * rarity_data["multipliers"][rarity])
    
    # Create different types of items
    if item_type == "weapon":
        weapon_types = ["Sword", "Axe", "Dagger", "Mace", "Staff", "Bow"]
        if weapon_set_type:
            weapon_type = weapon_set_type
            # Import weapon_special_attacks from data
            from data import weapon_special_attacks
            special_attacks = weapon_special_attacks.get(weapon_type, None)
        else:
            weapon_type = item_name if item_name in weapon_types else random.choice(weapon_types)
            special_attacks = None
        return create_weapon(level, rarity, prefix, weapon_type, value_base, rarity_data, special_attacks=special_attacks)
        
    elif item_type == "armor":
        armor_types = ["Helmet", "Chestplate", "Gauntlets", "Leggings", "Boots", "Shield"]
        armor_type = item_name if item_name in armor_types else random.choice(armor_types)
        return create_armor(level, rarity, prefix, armor_type, value_base, rarity_data, armor_set_type)
        
    elif item_type in ["ring", "amulet", "belt"]:
        return create_accessory(level, rarity, prefix, item_type, value_base, rarity_data)
        
    elif item_type == "potion":
        return create_potion(level, rarity, prefix, item_name, value_base, rarity_data)
        
    else:
        raise ValueError(f"Invalid item type: {item_type}")

def generate_item_by_name(name, item_type):
    """Recreate an item based on its name and type from save data."""
    item_dict = {
        "Weapon": [
            Weapon("Iron Sword", "A sturdy iron sword.", 50, 5),
            Weapon("Battle Axe", "A heavy axe with a sharp blade.", 75, 7),
            Weapon("Steel Sword", "A sharp steel sword.", 100, 8),
            Weapon("War Hammer", "A heavy hammer that crushes enemies.", 120, 10)
        ],
        "Armor": [
            Armor("Leather Armor", "Light armor offering basic protection.", 40, 3),
            Armor("Chainmail", "Stronger armor made of interlocking metal rings.", 70, 5),
            Armor("Knight's Plate", "Heavy armor for maximum protection.", 150, 10),
            Armor("Dragon Scale Armor", "Rare armor made from dragon scales.", 200, 12)
        ],
        "Potion": [
            Potion("Healing Potion", "Restores 30 HP.", 30, "heal", 30),
            Potion("Greater Healing Potion", "Restores 50 HP.", 50, "heal", 50),
            Potion("Mighty Strength Potion", "Boosts attack by 5 for a short time.", 60, "attack_boost", 5),
            Potion("Stone Skin Potion", "Increases defense by 5 temporarily.", 60, "defense_boost", 5)
        ]
    }

    for item in item_dict.get(item_type, []):
        if item.name == name:
            return item  # Return the matching item
    
    print(f"{Colors.RED}Warning: Item '{name}' of type '{item_type}' not found!{Colors.RESET}")
    return None  # Return None if no match is found


def display_inventory(player):
    """Display the player's inventory with options to use or equip items"""
    while True:
        clear_screen()
        print(f"\n{Colors.YELLOW}{Colors.BOLD}╔═══════════════════ INVENTORY ═══════════════════╗{Colors.RESET}")
        print(f"{Colors.YELLOW}║ Gold: {player.gold}{' ' * (45 - len(str(player.gold)) - 7)}║{Colors.RESET}")
        print(f"{Colors.YELLOW}╠═══════════════════════════════════════════════════╣{Colors.RESET}")
        
        if not player.inventory:
            print(f"{Colors.YELLOW}║ {Colors.RED}Your inventory is empty.{' ' * 24}║{Colors.RESET}")
        else:
            for i, item in enumerate(player.inventory, 1):
                # Truncate item name if too long
                item_str = str(item)
                if len(item_str) > 45:
                    item_str = item_str[:42] + "..."
                
                print(f"{Colors.YELLOW}║ {Colors.CYAN}{i}. {item_str}{' ' * (43 - len(str(i)) - len(item_str))}║{Colors.RESET}")
        
        print(f"{Colors.YELLOW}╚═══════════════════════════════════════════════════╝{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}What would you like to do?{Colors.RESET}")
        print(f"{Colors.YELLOW}1. Use/Equip Item{Colors.RESET}")
        print(f"{Colors.GREEN}2. Sort Inventory{Colors.RESET}")
        print(f"{Colors.MAGENTA}3. Discard Item{Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}0. Back{Colors.RESET}")
        
        choice = input(f"\n{Colors.CYAN}Enter choice: {Colors.RESET}")
        
        if choice == "0":
            break
        
        elif choice == "1" and player.inventory:
            try:
                item_num = int(input(f"{Colors.YELLOW}Enter item number to use/equip (0 to cancel): {Colors.RESET}"))
                if 1 <= item_num <= len(player.inventory):
                    item = player.inventory[item_num - 1]
                    
                    if isinstance(item, Potion):
                        item.use(player)
                        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
                    
                    elif isinstance(item, Weapon):
                        if player.equipped_weapon:
                            player.inventory.append(player.equipped_weapon)
                            print(f"{Colors.YELLOW}You unequip your {player.equipped_weapon.name}.{Colors.RESET}")
                        
                        player.equipped_weapon = item
                        player.inventory.remove(item)
                        print(f"{Colors.GREEN}You equip the {item.name}.{Colors.RESET}")
                        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
                    
                    elif isinstance(item, Armor):
                        if player.equipped_armor:
                            player.inventory.append(player.equipped_armor)
                            print(f"{Colors.YELLOW}You unequip your {player.equipped_armor.name}.{Colors.RESET}")
                        
                        player.equipped_armor = item
                        player.inventory.remove(item)
                        print(f"{Colors.GREEN}You equip the {item.name}.{Colors.RESET}")
                        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
            except ValueError as e:
                logger.warning(f"Invalid number input: {e}")
                print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "2" and player.inventory:
            print(f"\n{Colors.CYAN}Sort by:{Colors.RESET}")
            print(f"{Colors.YELLOW}1. Type{Colors.RESET}")
            print(f"{Colors.GREEN}2. Value{Colors.RESET}")
            print(f"{Colors.MAGENTA}3. Name{Colors.RESET}")
            
            sort_choice = input(f"\n{Colors.CYAN}Enter choice: {Colors.RESET}")
            
            if sort_choice == "1":
                # Sort by type: Potions, Weapons, Armor
                player.inventory.sort(key=lambda x: (isinstance(x, Armor), isinstance(x, Weapon), isinstance(x, Potion)))
                print(f"{Colors.GREEN}Inventory sorted by type.{Colors.RESET}")
            
            elif sort_choice == "2":
                # Sort by value (highest first)
                player.inventory.sort(key=lambda x: x.value, reverse=True)
                print(f"{Colors.GREEN}Inventory sorted by value.{Colors.RESET}")
            
            elif sort_choice == "3":
                # Sort by name
                player.inventory.sort(key=lambda x: x.name)
                print(f"{Colors.GREEN}Inventory sorted by name.{Colors.RESET}")
            
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "3" and player.inventory:
            try:
                item_num = int(input(f"{Colors.YELLOW}Enter item number to discard (0 to cancel): {Colors.RESET}"))
                if 1 <= item_num <= len(player.inventory):
                    item = player.inventory[item_num - 1]
                    confirm = input(f"{Colors.RED}Are you sure you want to discard {item.name}? (y/n): {Colors.RESET}")
                    
                    if confirm.lower() == "y":
                        player.inventory.remove(item)
                        print(f"{Colors.RED}You discard the {item.name}.{Colors.RESET}")
                        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
            except ValueError as e:
                logger.warning(f"Invalid number input: {e}")
                print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

