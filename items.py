__version__ = "262.0"
__creation__ = "9-03-2025"

import random

from colors import Colors
from game_utility import clear_screen
from data import enemy_sets

debug = 0

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
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value
    
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
            defense = extras.get("bonuses", {}).get("defense", 0)
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

        # Pour les autres types d'items (ex : consommables spéciaux)
        return item_type(data["name"], data["description"], data["value"], **extras)

class Gear(Item):
    """Gère les objets équipables (armes, armures, anneaux, etc.)."""
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


class Equipment:
    """Gère l'équipement du joueur (slots et bonus appliqués)."""
    def __init__(self, **kwargs):
        """Initialise les slots de l'équipement."""
        self.slots = {
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
                from items import Item
                eq.slots[slot] = Item.from_dict(item_data)
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
        
        if slot not in self.slots:
            print(f"{Colors.RED}ERROR: Invalid slot '{slot}' for {item.name}!{Colors.RESET}")
            return

        # Vérifie si un objet est déjà équipé et le déséquipe
        if self.slots[slot]:
            self.unequip(slot, player)

        # Équipe le nouvel objet
        self.slots[slot] = item
        print(f"{Colors.GREEN}Equipped {item.name} in {slot}.{Colors.RESET}")

        # Met à jour les statistiques du joueur
        player.stats.update_total_stats()
        player.calculate_set_bonus()


    def unequip(self, slot, player):
        """Déséquipe un objet d'un slot."""
        if slot in self.slots and self.slots[slot]:
            removed_item = self.slots[slot]
            self.slots[slot] = None
            print(f"{Colors.YELLOW}Unequipped {removed_item.name} from {slot}.{Colors.RESET}")
            player.stats.update_total_stats()
            return removed_item
        print(f"{Colors.RED}No item equipped in {slot}.{Colors.RESET}")
        return None

    def get_equipped_items(self):
        """Retourne tous les objets actuellement équipés."""
        return {slot: item for slot, item in self.slots.items() if item}


class Weapon(Gear):
    """
    Représente une arme équipable qui augmente les dégâts d'attaque.
    Hérite de Gear pour être compatible avec le système d'équipement.
    """
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value, {"attack": damage})
        self.damage = damage
    
    def __str__(self):
        return f"{self.name} - {self.description} (Damage: +{self.damage}, Value: {self.value} gold)"
    
    def to_dict(self):
        """Convertit l'arme en dictionnaire pour la sauvegarde."""
        data = super().to_dict()
        data["extra"]["damage"] = self.damage
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crée une arme à partir d'un dictionnaire sans modifier le format général."""
        extras = data.get("extra", {})
        return Weapon(
            data["name"],
            data["description"],
            data["value"],
            extras.get("damage", 0)
        )


class Armor(Gear):
    """Represents an equippable armor piece that enhances defense."""
    def __init__(self, name, description, value, defense, armor_type):
        super().__init__(name, description, value, {"defense": defense})
        self.armor_type = armor_type  # "helmet", "chestplate", "leggings", etc.

    def to_dict(self):
        data = super().to_dict()
        data["extra"]["armor_type"] = self.armor_type
        return data


class Shield(Gear):
    """Represents an equippable shield that provides high defense and blocking."""
    def __init__(self, name, description, value, defense, block_chance):
        super().__init__(name, description, value, {"defense": defense})
        self.block_chance = block_chance  # Chance de bloquer une attaque (ex: 20%)

    def to_dict(self):
        data = super().to_dict()
        data["extra"]["block_chance"] = self.block_chance
        return data


class Gauntlets(Gear):
    """Represents an equippable gauntlet that increases strength and defense."""
    def __init__(self, name, description, value, defense, strength_boost):
        super().__init__(name, description, value, {"defense": defense, "strength": strength_boost})
    
    def apply_effect(self, player):
        """Applique les effets des gants au joueur."""
        for stat, bonus in self.effect.items():
            player.stats.__dict__[stat] += bonus
    
    def __str__(self):
        return f"{self.name} - {self.description} (Defense: +{self.defense}, Effects: {self.effect}, Value: {self.value} gold)"

    def to_dict(self):
        return super().to_dict()


class Amulet(Gear):
    """Represents an equippable amulet with magical bonuses."""
    def __init__(self, name, description, value, effects):
        super().__init__(name, description, value, effects)

class Ring(Gear):
    """Represents an equippable ring that grants magical or stat bonuses."""
    def __init__(self, name, description, value, effects):
        super().__init__(name, description, value, effects)

class Belt(Gear):
    """Represents an equippable belt that boosts stamina or defense."""
    def __init__(self, name, description, value, effects):
        super().__init__(name, description, value, effects)


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
        
        if self.effect_type == "heal":
            old_hp = player.stats.hp
            player.heal(self.effect_value)
            print(f"{Colors.GREEN}You drink the {self.name} and recover {player.stats.hp - old_hp} HP!{Colors.RESET}")
            if debug >= 1:
                print(f'{Colors.RED}DEBUG: old_hp: {old_hp}\nplayer.stats.hp: {player.stats.hp}')
        elif self.effect_type == "attack_boost":
            player.stats.temporary_stats["attack"] += self.effect_value
            print(f"{Colors.RED}You drink the {self.name} and feel stronger! Attack +{self.effect_value}{Colors.RESET}")
        elif self.effect_type == "defense_boost":
            player.stats.temporary_stats["defense"] += self.effect_value
            print(f"{Colors.BLUE}You drink the {self.name} and feel tougher! Defense +{self.effect_value}{Colors.RESET}")
        elif self.effect_type == "luck_boost":
            player.stats.temporary_stats["luck"] += self.effect_value
            print(f"{Colors.CYAN}You drink the {self.name} and feel luckier! Luck +{self.effect_value}{Colors.RESET}")
        
        # Remove from inventory after use
        try:
            player.inventory.remove(self)
        except ValueError:
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


def generate_random_item(player=None, enemy=None, item_type=None, rarity=None, item_name=None, rarity_boost=None, available_rarities=None, level_boost=0, enemy_type=None):
    """Generate a specific or random item with customizable attributes.

    Parameters:
        player (class Player) to get automatically the level and difficulty
        item_type (str, optional): "weapon", "armor", or "potion". Default is random.
        rarity (str, optional): Specify rarity ("common", "epic", etc.), or random.
        item_name (str, optional): Choose a specific item (e.g., "Sword", "Helmet").
        rarity_boost (float, optional): Adjusts drop rates for rare items. Default is 1.0.
        available_rarities (list, optional): List of available rarities. Default is ["common", "uncommon", "rare", "epic", "legendary", "divine"]
        enemy_type (str, optional): 
            - Goblin / Goblin King
            - Skeleton / Skeleton Lord
            - Wolf / Alpha Dire Wolf
            - Orc / Orc Warlord
            - Troll / Ancient Troll
            - Ghost / Spectre Lord
            - Dark Elf / Dark Elf Queen
            - Wraith / Wraith King
            - Golem / Ancient Golem
            - Dragon Whelp / Elder Dragon
            - Demon / Dark Lord
            - Dark Shape / Senessax

    Returns:
        Item (Weapon, Armor, or Potion)
    """
    global debug
    debug = 0

    level = (player.dungeon_level + level_boost) if player else 1
    difficulty = player.difficulty if player else "normal"
    
    if not enemy_type:
        if enemy:
            enemy_type = enemy.type
        else:
            enemy_type = None
            if debug >= 1:
                print(f"{Colors.RED}Not enemy_type{Colors.RESET}")
    elif enemy_type not in enemy_sets:
        print(f"{Colors.RED}enemy_type: {enemy_type} not in enemy_sets{Colors.RESET}")
        enemy_type = None
    else:
        # print(f"{Colors.RED}enemy_type = None")
        enemy_type = None

    if debug >= 1:
        print('DEBUG: Given item_type:', item_type)

    if available_rarities is None:
        if difficulty == "normal":
            available_rarities = ["common", "uncommon", "rare", "epic", "legendary", "divine"]
        elif difficulty == "soul_enjoyer":
            available_rarities = ["common", "uncommon", "rare", "epic", "legendary"]
        elif difficulty == "realistic":
            available_rarities = ["common", "uncommon", "rare", "epic", "legendary", "divine", "???"]
        else:
            available_rarities = ["common", "uncommon", "rare", "epic", "legendary", "divine"]
            print(difficulty)
            print(available_rarities)

        # Adapte les rareté au niveaux (niv 1 on ne peut avoir mieux : rare, niv 2: rareté max = epic...)
        if level <= len(available_rarities):  
            available_rarities = available_rarities[:level + 2]  # Assure que la liste ne devient pas vide
            if debug >= 1:
                print("rarity penality due to low dungenon level. Available rarity for your dungenon level: ", available_rarities)


    elif available_rarities not in ["common", "uncommon", "rare", "epic", "legendary", "divine", "???"]:
        print('invalid rarity called in generate_random_item')


    if rarity_boost is None:
        if difficulty == "normal":
            rarity_boost = 1.0
        elif difficulty == "soul_enjoyer":
            rarity_boost = 0.8
        elif difficulty == "realistic":
            rarity_boost = 0.5
        else:
            print(difficulty)
            print('Rarity_boost is not none and difficult is invalid (item/def generate_random_item())')
            try:
                print(rarity_boost)
            except Exception as e:
                print(e)

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

    # Filtrer les raretés disponibles qui existent bien dans les poids normalisés
    valid_rarities = [r for r in available_rarities if r in normalized_weights]

    # Vérifier que la liste des raretés disponibles n'est pas vide
    if not valid_rarities:
        print(f"{Colors.RED}ERROR: No valid rarities available! Defaulting to 'common'.{Colors.RESET}")
        rarity = "common"
    else:
        # Sélectionner une rareté avec les probabilités ajustées
        rarity = random.choices(
            valid_rarities, 
            weights=[normalized_weights[r] for r in valid_rarities]
        )[0]


    # Scaling multipliers for rarities
    rarity_multiplier = {
        "common": 1,
        "uncommon": 1.5,
        "rare": 2,
        "epic": 3,
        "legendary": 5,
        "divine": 10,
        "???": 100
    }

    # Color coding for rarity
    rarity_color = {
        "common": Colors.WHITE,
        "uncommon": Colors.GREEN,
        "rare": Colors.BLUE,
        "epic": Colors.MAGENTA,
        "legendary": Colors.YELLOW,
        "divine": Colors.rainbow_text,
        "???": lambda text: Colors.gradient_text(text, (0, 0, 0), (255, 0, 0))  # Black to red gradient
    }

    # Base value scaling with level and rarity
    value_base = int(50 * level * rarity_multiplier[rarity])

    # Prefix based on rarity
    rarity_prefixes = {
        "common": ["Common", "Basic", "Standard", "Ordinary", "Usual", "Normal"],
        "uncommon": ["Uncommon","Sharp", "Sturdy", "Reliable", "Balanced"],
        "rare": ["Rare", "Advanced", "Superior"],
        "epic": ["Epic", "Exceptional", "Impressive", "Masterwork"],
        "legendary": ["Legendary", "Ancient", "Mythical", "Enchanted"],
        "divine": ["Divine", "Holy", "Sacred", "Blessed", "Miraculous", "Supernatural", "Celestial"],
        "???": ["Unknown"]
    }
    if rarity in rarity_prefixes:
        prefix = random.choice(rarity_prefixes.get(rarity, [""]))
    else:
        prefix = ""
        print('Rarity in rarity_prefixes, rarity:', rarity, 'not in prefix:',rarity_prefixes)
        input('enter to continue..')

    # Définir les sets possibles
    """
    if enemy:
        if enemy in enemy_sets:
            set_type = enemy_sets[enemy]
            armor_set_type = set_type["armor"]
            weapon_set_type = set_type["weapon"]
        elif enemy not in enemy_sets:
            print(f"{Colors.RED}Enemy \"{enemy}\" not found in enemy_sets{Colors.RESET}")
            print(enemy_sets)
            armor_set_type = ""
            weapon_set_type = ""
        else:
            armor_set_type = ""
            weapon_set_type = ""
    else:
        armor_set_type = ""
        weapon_set_type = ""
    """
    
    if enemy_type and enemy_type in enemy_sets:
        set_type = enemy_sets[enemy_type]
        armor_set_type = set_type.get("armor", "")
        weapon_set_type = set_type.get("weapon", "")
    else:
        if enemy_type:
            print(f"{Colors.RED}Enemy type \"{enemy_type}\" not found in enemy_sets{Colors.RESET}")
            print(enemy_sets)
        armor_set_type = ""
        weapon_set_type = ""


    # Determine item type if not specified
    if enemy_type:
        item_type = random.choice(["armor", "weapon"])
        if debug >= 1:
            print('DEBUG: enemy -> random item_type:', item_type)

    elif item_type is None:
        item_type = random.choice(["weapon", "armor", "potion", "ring", "amulet", "belt"])
        if debug >= 1:
            print('DEBUG: item_type is None -> random item_type:', item_type)

    if debug >= 1:
        print('DEBUG: Final item_type:', item_type)

    if item_type == "weapon":
        # Default weapon choices
        weapon_types = ["Sword", "Axe", "Dagger", "Mace", "Staff", "Bow"]
        
        if weapon_set_type:
            weapon_type = weapon_set_type
        else:
            weapon_type = item_name if item_name in (weapon_types or weapon_set_type) else random.choice(weapon_types)
        
        damage = int((1 + level) * rarity_multiplier[rarity])
        
        name = f"{prefix} {weapon_type}"

        # Trouver la rareté correspondante au préfixe
        rarity_key = next((key for key, values in rarity_prefixes.items() if prefix in values), rarity)
        # Appliquer la couleur correcte en fonction de la rareté trouvée
        colored_name = rarity_color[rarity_key](name) if callable(rarity_color[rarity_key]) else f"{rarity_color[rarity_key]}{name}{Colors.RESET}"
        
        desc = f"A level {level} {prefix} weapon"
        return Weapon(colored_name, desc, value_base, damage)

    elif item_type in ["armor", "ring", "amulet", "belt"]:
        if item_type == "armor":
            # Default armor choices
            armor_types = [
                "Helmet", "Chestplate", "Gauntlets",
                "Leggings", "Boots", "Shield"
                ]
            
            if armor_set_type:
                name_prefix = f"{prefix} {armor_set_type}"
            else:
                name_prefix = f"{prefix}"

            armor_type = item_name if item_name in armor_types else random.choice(armor_types)
            defense = int((2 + level) * rarity_multiplier[rarity])

            name = f"{name_prefix} {armor_type}"
            colored_name = rarity_color[rarity](name) if callable(rarity_color[rarity]) else f"{rarity_color[rarity]}{name}{Colors.RESET}"
            desc = f"A level {level} {prefix} armor piece"
            return Armor(colored_name, desc, value_base, defense, armor_type)
        
        elif item_type == "ring":
            effect = {"luck": int(1 * rarity_multiplier[rarity])}
            name = f"{prefix} Ring"
            colored_name = rarity_color[rarity](name) if callable(rarity_color[rarity]) else f"{rarity_color[rarity]}{name}{Colors.RESET}"
            desc = f"A magical ring that enhances luck"
            return Ring(colored_name, desc, value_base, effect)

        elif item_type == "amulet":
            effect = {"defense": int(2 * rarity_multiplier[rarity])}
            name = f"{prefix} Amulet"
            colored_name = rarity_color[rarity](name) if callable(rarity_color[rarity]) else f"{rarity_color[rarity]}{name}{Colors.RESET}"
            desc = f"A mystical amulet that grants protection"
            return Amulet(colored_name, desc, value_base, effect)
        
        elif item_type == "belt":
            effect = {"agility": int(1 * rarity_multiplier[rarity])}
            name = f"{prefix} Belt"
            colored_name = rarity_color[rarity](name) if callable(rarity_color[rarity]) else f"{rarity_color[rarity]}{name}{Colors.RESET}"
            desc = f"A sturdy belt that enhances movement speed"
            return Belt(colored_name, desc, value_base, effect)


    elif item_type == "potion":
        # Default potion choices
        potion_types = {
            "Healing Potion": {"effect_type": "heal", "effect_value": int(20 * level * rarity_multiplier[rarity])},
            "Strength Elixir": {"effect_type": "attack_boost", "effect_value": int(2 * rarity_multiplier[rarity])},
            "Iron Skin Tonic": {"effect_type": "defense_boost", "effect_value": int(2 * rarity_multiplier[rarity])},
            "Lucky Charm Brew": {"effect_type": "luck_boost", "effect_value": int(1 * rarity_multiplier[rarity])},
            "Healing Spring Potion": {"effect_type": "heal", "effect_value": int(10 * rarity_multiplier[rarity])},
            "Dragon's Breath Potion": {"effect_type": "fire_damage", "effect_value": int(1 * rarity_multiplier[rarity])}
        }

        # Choose specific potion or random one
        potion_name = item_name if item_name in potion_types else random.choice(list(potion_types.keys()))
        potion = potion_types[potion_name]

        name = f"{prefix} {potion_name}"
        colored_name = rarity_color[rarity](name) if callable(rarity_color[rarity]) else f"{rarity_color[rarity]}{name}{Colors.RESET}"
        effect_desc = {
            "heal": f"Restores {potion['effect_value']} HP",
            "attack_boost": f"Increases Attack by {potion['effect_value']}",
            "defense_boost": f"Increases Defense by {potion['effect_value']}",
            "luck_boost": f"Increases Luck by {potion['effect_value']}"
        }.get(potion["effect_type"], "")

        return Potion(colored_name, effect_desc, value_base, potion["effect_type"], potion["effect_value"])

    else:
        print(f"{Colors.RED}Invalid item type: {item_type}{Colors.RESET}")
        return None


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
            
            except ValueError:
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
            
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
