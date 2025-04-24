import random
import json
import os

from colors import Colors
from game_utility import clear_screen, handle_error
from items import Item, Equipment, Gear, Weapon, Armor, Ring, Amulet, Belt, Potion
from data import armor_sets, enemy_types, boss_types
from quests import Quest

debug = 0

class StatContainer: # Pas encore utilsé
    """Classe pour gérer les stats permanentes et temporaires avec accès en notation pointée."""
    def __init__(self, base_stats):
        self.__dict__.update({key: 0 for key in base_stats})

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return str(self.__dict__)

class Stats:
    """Gère les stats du joueur avec des effets permanents et temporaires."""
    def __init__(self, equipment=None, **kwargs):
        """Initialisation des stats avec gestion des erreurs."""
        self.equipment = equipment # Stockage de l'équipment
        self.permanent_stats = {
            "hp": 100, "max_hp": 100,
            "attack": 10, "defense": 5,
            "magic_damage": 1, "magic_defense": 1,
            "agility": 5, "luck": 5,
            "mana": 20, "max_mana": 20,
            "stamina": 50, "max_stamina": 50,
            "critical_chance": 5
        }

        # Appliquer les valeurs passées en argument
        for key, value in kwargs.items():
            if key in self.permanent_stats and isinstance(value, (int, float)):
                self.permanent_stats[key] = value  # Assure que seules les valeurs valides sont appliquées

        # Initialisation des stats temporaires
        self.temporary_stats = {key: 0 for key in self.permanent_stats}

        # Vérification pour éviter toute corruption des stats permanentes
        for key, value in self.permanent_stats.items():
            if not isinstance(value, (int, float)):  
                print(f"{Colors.RED}ERROR: permanent_stats[{key}] has an invalid type ({type(value)}). Resetting to 0.{Colors.RESET}")
                self.permanent_stats[key] = 0  

        # Vérification pour éviter toute corruption des stats temporaires
        if not isinstance(self.temporary_stats, dict):
            print(f"{Colors.RED}ERROR: temporary_stats is corrupted! Resetting...{Colors.RESET}")
            self.temporary_stats = {key: 0 for key in self.permanent_stats}

        # Initialisation des stats visibles
        self.update_total_stats()

        # print(f"DEBUG: Permanent stats: {self.permanent_stats}")
        # print(f"DEBUG: Temporary stats: {self.temporary_stats}")

    def __repr__(self):
        """Affiche les stats avec permanent, temporaire et équipement."""
        equipment_bonuses = {key: 0 for key in self.permanent_stats}

        if hasattr(self, "equipment") and isinstance(self.equipment, Equipment):
            for slot, item in self.equipment.slots.items():
                if isinstance(item, Gear):  
                    for stat, value in item.effects.items():
                        if stat in equipment_bonuses:
                            equipment_bonuses[stat] += value
                        else:
                            equipment_bonuses[stat] = value

        # Affichage structuré
        return (
            f"Permanent: {self.permanent_stats}\n"
            f"Temporary: {self.temporary_stats}\n"
            f"Equipment: {equipment_bonuses}\n"
        )

    
    def __getattr__(self, key):
        """Permet d'accéder directement à la valeur combinée des stats permanentes et temporaires."""
        if key in self.permanent_stats:
            return self.permanent_stats[key] + self.temporary_stats.get(key, 0)
        raise AttributeError(f"'Stats' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        """Si on modifie une stat existante, elle est ajoutée aux stats permanentes."""
        if "permanent_stats" in self.__dict__ and key in self.permanent_stats:
            self.permanent_stats[key] = value  # Modifie directement les stats permanentes
        else:
            super().__setattr__(key, value)  # Utilisation normale pour les autres attributs

    def update_total_stats(self):
        """Met à jour les stats visibles en combinant les permanentes, temporaires et équipements."""
        global debug
        debug = 0

        # Vérification stricte des stats de base
        if not isinstance(self.permanent_stats, dict):
            print(f"{Colors.RED}ERROR: permanent_stats is corrupted! Resetting...{Colors.RESET}")
            if debug >= 1:
                print(f"DEBUG: Stats: {self.permanent_stats}")
            self.permanent_stats = {
                "hp": 100, "max_hp": 100, "attack": 10, "defense": 5,
                "magic_damage": 1, "magic_defense": 1, "agility": 5, "luck": 5,
                "mana": 20, "max_mana": 20, "stamina": 50, "max_stamina": 50,
                "critical_chance": 5
            }
            if debug >= 1:
                print(f"DEBUG: Stats: {self.permanent_stats}")

        if not isinstance(self.temporary_stats, dict):
            print(f"{Colors.RED}ERROR: temporary_stats is corrupted! Resetting...{Colors.RESET}")
            if debug >= 1:
                print(f"DEBUG: Stats: {self.permanent_stats}")
            self.temporary_stats = {key: 0 for key in self.permanent_stats}
            if debug >= 1:
                print(f"DEBUG: Stats: {self.permanent_stats}")

        # Vérification des types des stats
        for key in self.permanent_stats:
            if not isinstance(self.permanent_stats[key], (int, float)):
                print(f"{Colors.RED}ERROR: permanent_stats[{key}] is invalid ({type(self.permanent_stats[key])}). Resetting to 0.{Colors.RESET}")
                self.permanent_stats[key] = 0

            if not isinstance(self.temporary_stats.get(key, 0), (int, float)):
                print(f"{Colors.RED}ERROR: temporary_stats[{key}] is invalid ({type(self.temporary_stats.get(key, 0))}). Resetting to 0.{Colors.RESET}")
                self.temporary_stats[key] = 0

        # STOCKAGE GLOBAL DES BONUS D'ÉQUIPEMENT
        self.equipment_bonuses = {key: 0 for key in self.permanent_stats}

        # Vérifier si l'équipement existe
        if debug >= 1:
            print('self: ',self)
            print('self.equipment: ', self.equipment, 'self.equipment type:', type(self.equipment))
        # Vérifier que self.equipment est un dictionnaire
        if isinstance(self.equipment, Equipment) and isinstance(self.equipment.slots, dict):
            if debug >= 1:
                print(f"{Colors.CYAN}DEBUG: Equipment found, processing bonuses...{Colors.RESET}")  

            # Appliquer TOUS les effets des équipements
            for slot, item in self.equipment.slots.items():
                if item is None:
                    if debug >= 1:
                        print(f"{Colors.YELLOW}DEBUG: Slot {slot} is empty (None). Skipping...{Colors.RESET}")
                    continue  # Ignorer les slots vides
                
                if isinstance(item, Gear):  # Vérifier que c'est bien un objet Gear
                    if debug >= 1:
                        print(f"{Colors.CYAN}DEBUG: Processing {slot}: {item.name}...{Colors.RESET}")  

                    for stat, value in item.effects.items():
                        if debug >= 1:
                            print(f"{Colors.CYAN}DEBUG: {slot} gives {stat}: +{value}{Colors.RESET}")  

                        if stat in self.equipment_bonuses:
                            self.equipment_bonuses[stat] += value
                        else:
                            self.equipment_bonuses[stat] = value  # Si la stat n'existait pas encore
                else:
                    print(f"{Colors.RED}ERROR: Unexpected item in {slot}: {item} (Type: {type(item)}){Colors.RESET}")

            if debug >= 1:
                print(f"{Colors.GREEN}DEBUG: Final Equipment Bonuses -> {self.equipment_bonuses}{Colors.RESET}")  
        elif self.equipment is None:
            if debug >= 1:
                print(f"{Colors.YELLOW}DEBUG: No equipment found. Skipping...{Colors.RESET}")
        else:
            print(f"{Colors.RED}ERROR: self.equipment is not a dictionary! Type: {type(self.equipment)}{Colors.RESET}")


        # MISE À JOUR DES STATS VISIBLES
        self.__dict__.update({
            key: self.permanent_stats[key] + self.temporary_stats.get(key, 0) + self.equipment_bonuses.get(key, 0)
            for key in self.permanent_stats
        })

        if debug >= 1:
            print(f"{Colors.CYAN}DEBUG: Updated total stats -> {self.__dict__}{Colors.RESET}")
            print(f"{Colors.YELLOW}DEBUG: Equipment Bonuses Stored -> {self.equipment_bonuses}{Colors.RESET}")
            input()


    def modify_stat(self, stat_name, value, permanent=True):
        """Modifie une stat de façon permanente ou temporaire."""
        global debug
        if stat_name in self.permanent_stats:
            if permanent:
                self.permanent_stats[stat_name] += value
            else:
                self.temporary_stats[stat_name] += value  # Ajout temporaire
            
            # Mise à jour des stats visibles
            self.update_total_stats()

            if debug >= 1:
                print(f"{Colors.GREEN}{stat_name.capitalize()} changed by {value}! (Now {self.__dict__[stat_name]}){Colors.RESET}")
        else:
            print(f"{Colors.RED}Stat {stat_name} does not exist!{Colors.RESET}")

    def remove_temporary_effects(self):
        """Réinitialise toutes les stats temporaires à 0 et met à jour les stats visibles."""
        global debug

        if not isinstance(self.temporary_stats, dict):
            print(f"{Colors.RED}ERROR: temporary_stats is corrupted! Resetting...{Colors.RESET}")
            self.temporary_stats = {key: 0 for key in self.permanent_stats}

        for key in self.temporary_stats:
            self.temporary_stats[key] = 0

        self.update_total_stats()
        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Temporary effects removed. Stats updated.{Colors.RESET}")

    def take_damage(self, damage):
        """Gère la prise de dégâts en priorisant les points de vie temporaires et conserve les HP max temporaires."""
        global debug

        # Vérification de la structure des stats avant utilisation
        if not isinstance(self.temporary_stats, dict):
            print(f"{Colors.RED}ERROR: temporary_stats is corrupted! Resetting...{Colors.RESET}")
            self.temporary_stats = {key: 0 for key in self.permanent_stats}

        if not isinstance(self.permanent_stats, dict):
            print(f"{Colors.RED}ERROR: permanent_stats is corrupted! Resetting...{Colors.RESET}")
            self.permanent_stats = {
                "hp": 100, "max_hp": 100, "attack": 10, "defense": 5,
                "magic_damage": 1, "magic_defense": 1, "agility": 5, "luck": 5,
                "mana": 20, "max_mana": 20, "stamina": 50, "max_stamina": 50,
                "critical_chance": 5
            }

        hp_temp = self.temporary_stats["hp"]
        hp_max_temp = self.temporary_stats["max_hp"]
        hp_perm = self.permanent_stats["hp"]

        # Dégâts absorbés en priorité par les HP temporaires
        if hp_temp > 0:
            damage_absorbed = min(hp_temp, damage)
            self.temporary_stats["hp"] -= damage_absorbed
            damage -= damage_absorbed  # Mise à jour des dégâts restants
        else:
            damage_absorbed = 0

        # S'il reste des dégâts, ils sont appliqués aux HP permanents
        if damage > 0:
            self.permanent_stats["hp"] = max(0, hp_perm - damage)

        # Mise à jour des HP affichés (permanents + temporaires)
        self.update_total_stats()

        if debug >= 1:
            print(f"DEBUG: After damage -> Temp HP: {self.temporary_stats['hp']}/{hp_max_temp},\n"
                f"Perm HP: {self.permanent_stats['hp']}/{self.permanent_stats['max_hp']}")
        
        # return total damage
        return damage, damage_absorbed


class Skill:
    """
    Represents a special skill with:
    - name: the name of the skill.
    - description: a description of the skill.
    - level: the mastery level of the skill.
    - damage_multiplier: multiplier applied to the base damage.
    - temporary_bonus: a dict of bonus effects (e.g., {"defense": 5}).
    - cost: a dict of resource costs (e.g., {"mana": 10, "stamina": 5, "hp": 0}).
    """
    def __init__(self, name, description, level=1, damage_multiplier=1, temporary_bonus=None, cost=None):
        self.name = name
        self.description = description
        self.level = level
        self.damage_multiplier = damage_multiplier
        self.temporary_bonus = temporary_bonus if temporary_bonus is not None else {}
        self.cost = cost if cost is not None else {}

    def to_dict(self):
        """Convertit l'objet Skill en dictionnaire automatiquement."""
        return self.__dict__.copy()

    def __str__(self):
        cost_str = ", ".join(f"{k}: {v}" for k, v in self.cost.items()) if self.cost else "No cost"
        bonus_str = ", ".join(f"{k}: +{v}" for k, v in self.temporary_bonus.items()) if self.temporary_bonus else "No bonus"
        return f"{self.name} (Lv{self.level}): {self.description} | Multiplier: {self.damage_multiplier} | Cost: {cost_str} | Bonus: {bonus_str}"

    def activate(self, player):
        """
        Activates the skill:
          - Checks if the player has enough resources (mana, stamina, hp) based on self.cost.
          - If not, prints an error and returns a multiplier of 0.
          - Otherwise, it deducts the cost and applies temporary bonuses.
          - Returns the damage multiplier of the skill.
        """
        # Vérifier que le joueur dispose des ressources nécessaires
        for resource, cost_value in self.cost.items():
            current_value = getattr(player.stats, resource, 0)
            if current_value < cost_value:
                print(f"{Colors.RED}You don't have enough {resource} to use {self.name}!{Colors.RESET}")
                return 0

        # Déduire le coût des ressources
        for resource, cost_value in self.cost.items():
            # Utilise la méthode modify_stat pour déduire la valeur (cost_value négatif)
            player.use_mana(cost_value)
                        
        # Appliquer les bonus temporaires
        for stat, bonus in self.temporary_bonus.items():
            player.modify_stat(stat, bonus)

        print(f"{Colors.GREEN}{self.name} activated!{Colors.RESET}")
        return self.damage_multiplier


skills_dict = {
    "Berserk Rage": Skill("Berserk Rage", "Unleash a furious attack.", level=1, damage_multiplier=2.0, temporary_bonus={}, cost={"stamina": 10}),
    "Shadow Strike": Skill("Shadow Strike", "A swift and deadly strike.", level=1, damage_multiplier=1.5, temporary_bonus={}, cost={"stamina": 8}),
    "Arcane Blast": Skill("Arcane Blast", "A powerful burst of arcane energy.", level=1, damage_multiplier=2.5, temporary_bonus={}, cost={"mana": 15}),
    "Divine Shield": Skill("Divine Shield", "Raises a protective barrier reducing damage.", level=1, damage_multiplier=1.0, temporary_bonus={"defense": 5}, cost={"mana": 10}),
    # more skills
    "Healing Wave": Skill("Healing Wave", "Heals yourself with some magics.", level=1, damage_multiplier=0.0, temporary_bonus={"hp": 10}, cost={"mana": 5}),
    "Shield Bash": Skill("Shield Bash", "Bashes the enemy with your shield.", level=1, damage_multiplier=1.0, temporary_bonus={"attack": 5}, cost={"stamina": 5}),
}


# Game Classes
class Entity:
    """
    Represents any character in the game (Player, Enemy, NPC).
    
    Attributes:
        name (str): The name of the entity.
        hp (int): Current health points.
        max_hp (int): Maximum health points.
        attack (int): Attack power of the entity.
        defense (int): Defensive value reducing incoming damage.

    Methods:
        is_alive() -> bool:
            Returns True if the entity's HP is above 0.
        
        take_damage(damage: int) -> int:
            Reduces HP based on incoming damage minus defense. Returns the actual damage taken.
        
        heal(amount: int) -> None:
            Restores HP up to the max_hp limit.
    """
    def __init__(self, name, hp, max_hp, attack, defense):
        self.name = name
        self.stats = Stats(
            hp=hp,
            max_hp=max_hp,
            attack=attack,
            defense=defense
        )
    
    def is_alive(self):
        return self.stats.hp > 0
    
    def heal(self, amount: int):
        """Soigne d'abord les HP permanents, puis les HP temporaires, sans dépasser le max."""
        global debug

        hp_perm = self.stats.permanent_stats["hp"]
        hp_max_perm = self.stats.permanent_stats["max_hp"]
        hp_temp = self.stats.temporary_stats["hp"]
        hp_max_temp = self.stats.temporary_stats["max_hp"]

        # Restaurer les HP permanents en premier
        heal_perm = min(amount, hp_max_perm - hp_perm)
        self.stats.permanent_stats["hp"] += heal_perm
        amount -= heal_perm  # Réduit le soin restant

        # Restaurer les HP temporaires si du soin reste
        if amount > 0:
            heal_temp = min(amount, hp_max_temp - hp_temp)
            self.stats.temporary_stats["hp"] += heal_temp

        # Met à jour les HP totaux
        self.stats.update_total_stats()

        if debug >= 1:
            print(f"DEBUG: Type of temporary_stats -> {type(self.stats.temporary_stats)}")
            print(f"DEBUG: temporary_stats content -> {self.stats.temporary_stats}")
            print(f"DEBUG: After healing -> Temp HP: {self.stats.temporary_stats['hp']}/{hp_max_temp}, "
                f"Perm HP: {self.stats.permanent_stats['hp']}/{hp_max_perm}")

"""    def heal(self, amount:int):
        self.stats.hp = min(self.stats.max_hp, self.stats.hp + amount)        
"""

"""
    def take_damage(self, damage, difficulty="normal"):
        """ #Handles taking damage, applying it permanently.
"""
        
        if difficulty == "soul_enjoyer":
            self.stats.permanent_stats["hp"] = 0  # Mort instantanée
            self.stats.hp = 0
            print(f"{Colors.RED}{self.name} took damage and died instantly!{Colors.RESET}")
        
        else:
            actual_damage = max(1, damage / max(1, self.stats.defense))  # Calcul des dégâts réduits par la défense
            
            print(f"DEBUG: Type of permanent_stats -> {type(self.stats.permanent_stats)}")
            print(f"DEBUG: permanent_stats content -> {self.stats.permanent_stats}")

            # Appliquer les dégâts à la stat permanente
            self.stats.permanent_stats["hp"] = max(0, self.stats.permanent_stats["hp"] - actual_damage)
            self.stats.hp = self.stats.permanent_stats["hp"]  # Synchroniser la stat temporaire
            
            print(f"DEBUG: {self.name} takes {actual_damage:.1f} damage!")
            print(f"DEBUG: {self.name} HP after damage: {self.stats.hp}/{self.stats.max_hp}")

            return actual_damage
"""


class Player(Entity):
    """
    Represents the player-controlled character.

    Inherits from:
        Entity (Base class for all characters)

    Attributes:
        level (int): The player's current level.
        xp (int): The player's experience points.
        gold (int): The player's gold currency.
        inventory (list): A list of items owned by the player.
        luck (int): Affects critical hits, rare item finds, and trap evasion.
        skills (list): A list of acquired skills.
        class_name (str): The player's chosen class specialization.
        max_xp (int): The required XP to level up.
        dungeon_level (int): The current depth level in the dungeon.
        profession (str | None): The player's profession (if applicable).
        quests (list): Active quests assigned to the player.
        completed_quests (list): Quests that have been finished.

    Methods:
        level_up() -> None:
            Increases stats and levels up the player.
        
        choose_class() -> None:
            Allows the player to pick a specialized class at level 5.
        
        gain_xp(amount: int) -> bool:
            Increases XP and checks if the player should level up.
        
        use_skill(target: Entity) -> int:
            Uses a learned skill on an enemy target.
        
        display_status() -> None:
            Prints the player's current stats and equipped items.
    """
    def __init__(self, name="Adventurer", difficulty="normal"):
        super().__init__(name, 100, 100, 5, 5)  # Héritage (si Player hérite d'une autre classe)

        self.level = 1
        self.xp = 0
        self.max_xp = 100
        self.gold = 50
        self.souls = 0

        self.inventory = [Potion("Minor Health Potion", "Restores some health", 10, "heal", 20)]

        # Équipement initialisé avant les stats (pour pouvoir l'envoyer dans Stats)
        self.equipment = Equipment(
            main_hand=None, off_hand=None, helmet=None, chest=None,
            gauntlets=None, leggings=None, boots=None, shield=None,
            ring=None, amulet=None, belt=None
        )


        # Création des stats en incluant l'équipement
        self.stats = Stats(equipment=self.equipment, 
                        hp=100, max_hp=100, attack=5, defense=5,
                        magic_damage=1, magic_defense=1, agility=5, luck=5,
                        mana=20, max_mana=20, stamina=50, max_stamina=50,
                        critical_chance=5)

        self.total_armor = 0
        self.set_bonuses = {}
        self.skills = []
        self.class_name = "Novice"
        self.dungeon_level = 1
        self.profession = None
        self.quests = []
        self.completed_quests = []
        self.kills = 0
        self.difficulty = difficulty

        self.unlocked_difficulties = {"normal": True, "soul_enjoyer": False, "realistic": False}
        self.finished_difficulties = {"normal": False, "soul_enjoyer": False, "realistic": False}

        # Met à jour les stats avec l'équipement initial (même s'il est vide)
        self.stats.update_total_stats()

        
        # print('DEBUG: Permanant_stats:', self.stats.permanent_stats)
        # input('press enter to continue')
        """
    def rest_stamina(self, amount:int):
        self.stats.stamina = min(self.stats.max_stamina, self.stats.stamina + amount)
    
    def regen_mana(self, amount:int):
        self.stats.mana = min(self.stats.max_mana, self.stats.mana + amount)
        """

    def rest_stamina(self, amount: int):
        """Régénère d'abord la stamina permanente, puis la stamina temporaire."""
        stamina_perm = self.stats.permanent_stats["stamina"]
        stamina_max_perm = self.stats.permanent_stats["max_stamina"]
        stamina_temp = self.stats.temporary_stats["stamina"]
        stamina_max_temp = self.stats.temporary_stats["max_stamina"]

        # Restaurer la stamina permanente en premier
        regen_perm = min(amount, stamina_max_perm - stamina_perm)
        self.stats.permanent_stats["stamina"] += regen_perm
        amount -= regen_perm  # Réduit la régénération restante

        # Restaurer la stamina temporaire si du soin reste
        if amount > 0:
            regen_temp = min(amount, stamina_max_temp - stamina_temp)
            self.stats.temporary_stats["stamina"] += regen_temp

        self.stats.update_total_stats()

    def use_stamina(self, amount: int):
        """Réduit la stamina en priorité sur les temporaires, puis les permanents."""
        stamina_temp = self.stats.temporary_stats["stamina"]
        stamina_perm = self.stats.permanent_stats["stamina"]

        # Diminuer la stamina temporaire en premier
        if stamina_temp > 0:
            used_temp = min(stamina_temp, amount)
            self.stats.temporary_stats["stamina"] -= used_temp
            amount -= used_temp

        # Si la stamina temporaire est vide, prendre sur la stamina permanente
        if amount > 0:
            self.stats.permanent_stats["stamina"] = max(0, stamina_perm - amount)

        self.stats.update_total_stats()


    def regen_mana(self, amount: int):
        """Régénère d'abord le mana permanent, puis le mana temporaire."""
        mana_perm = self.stats.permanent_stats["mana"]
        mana_max_perm = self.stats.permanent_stats["max_mana"]
        mana_temp = self.stats.temporary_stats["mana"]
        mana_max_temp = self.stats.temporary_stats["max_mana"]

        # Restaurer le mana permanent en premier
        regen_perm = min(amount, mana_max_perm - mana_perm)
        self.stats.permanent_stats["mana"] += regen_perm
        amount -= regen_perm

        # Restaurer le mana temporaire si du soin reste
        if amount > 0:
            regen_temp = min(amount, mana_max_temp - mana_temp)
            self.stats.temporary_stats["mana"] += regen_temp

        self.stats.update_total_stats()

    def use_mana(self, amount: int):
        """Réduit le mana en priorité sur les temporaires, puis les permanents."""
        mana_temp = self.stats.temporary_stats["mana"]
        mana_perm = self.stats.permanent_stats["mana"]

        # Diminuer le mana temporaire en premier
        if mana_temp > 0:
            used_temp = min(mana_temp, amount)
            self.stats.temporary_stats["mana"] -= used_temp
            amount -= used_temp

        # Si le mana temporaire est vide, prendre sur le mana permanent
        if amount > 0:
            self.stats.permanent_stats["mana"] = max(0, mana_perm - amount)

        self.stats.update_total_stats()


    def modify_stat(self, stat, bonus):
        self.stats.__dict__.update({stat: self.stats.__dict__[stat] + bonus})

    def equip_item(self, item):
        """Equip a weapon or armor piece in the correct slot automatically."""
        global debug
        debug = 1

        if isinstance(item, Weapon):
            # Vérifier si l'arme est déjà équipée
            if item in [self.equipment.main_hand, self.equipment.off_hand]:
                print(f"\n{Colors.RED}You have already equipped {item.name}!{Colors.RESET}")
                return

            # Vérifier si une main est libre pour équiper l'arme
            if not self.equipment.main_hand:
                self.equipment.main_hand = item
                print(f"\n{Colors.GREEN}You equipped {item.name} in your main hand!{Colors.RESET}")
            elif not self.equipment.off_hand:
                self.equipment.off_hand = item
                print(f"\n{Colors.GREEN}You equipped {item.name} in your off-hand!{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Both hands are occupied! Do you want to unequip an item first? (y/n){Colors.RESET}")
                choice = input(">>> ").lower()
                if choice == "y":
                    slot_choice = input(f"{Colors.YELLOW}Which hand do you want to unequip? (1: main_hand / 2: off_hand): {Colors.RESET}").lower()
                    if slot_choice in ['1', '2']:
                        slot_choice = "main_hand" if slot_choice == '1' else "off_hand"
                        self.unequip_item(slot_choice)
                        self.equipment.equip(slot=slot_choice, item=item, player=self)
                        print(f"\n{Colors.GREEN}You equipped {item.name} in your {slot_choice}!{Colors.RESET}")
                        self.inventory.remove(item)
                    else:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                return

            # Retirer l'arme de l'inventaire après l'avoir équipée
            if item in self.inventory:
                self.inventory.remove(item)

        elif isinstance(item, (Armor, Ring, Amulet, Belt)):
            armor_slot_map = {
                "Helmet": "helmet",
                "Chestplate": "chest",
                "Gauntlets": "gauntlets",
                "Leggings": "leggings",
                "Boots": "boots",
                "Shield": "shield",
                "Ring": "ring",
                "Amulet": "amulet",
                "Belt": "belt",
            }

            if isinstance(item, (Ring, Amulet, Belt)):  
                slot = armor_slot_map.get(item.__class__.__name__, None)  
                if debug > 1:
                    print(f"Slot for {item.__class__.__name__}: {slot}")
            else:
                slot = armor_slot_map.get(item.armor_type, None)  # Pour les armures classiques
                if debug > 1:
                    print(f"Slot for {item.armor_type}: {slot}")


            if slot:
                # Vérifier si le slot est déjà occupé
                if self.equipment.slots.get(slot):
                    print(f"\n{Colors.RED}{slot.capitalize()} is already occupied! Do you want to unequip it first? (y/n){Colors.RESET}")
                    choice = input(">>> ").lower()
                    if choice == "y":
                        self.unequip_item(slot)

                if debug >= 1:
                    print(f"Équipement avant: {self.equipment.slots}")  # Debug avant équipement
                self.equipment.equip(slot, item, self)
                if debug >= 1:
                    print(f"Équipement après: {self.equipment.slots}")  # Debug après équipement
                print(f"\n{Colors.GREEN}You equipped {item.name} in {slot}!{Colors.RESET}")
                self.inventory.remove(item)
            else:
                print(f"\n{Colors.RED}Invalid armor type: {item.armor_type}{Colors.RESET}")

        else:
            print(f"\n{Colors.YELLOW}You can't equip this item.{Colors.RESET}")

    def unequip_item(self, slot):
        """Déséquipe un objet (arme, armure, accessoire) et le remet dans l'inventaire."""
        if slot in self.equipment.slots and self.equipment.slots[slot]:
            item = self.equipment.unequip(slot, self)  # Utilise la méthode unequip de Equipment
            self.inventory.append(item)  # Remet l'objet dans l'inventaire
            print(f"\n{Colors.YELLOW}You unequipped {item.name} and placed it back in your inventory.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}No item equipped in {slot}.{Colors.RESET}")


    def unequip_item_menu(self):
        """Affiche un menu pour déséquiper un équipement."""
        equipped_items = {slot: item for slot, item in self.equipment.slots.items() if item}

        if not equipped_items:
            print(f"\n{Colors.RED}You have no equipped items to unequip!{Colors.RESET}")
            return

        print(f"\n{Colors.YELLOW}Equipped Items:{Colors.RESET}")
        for i, (slot, item) in enumerate(equipped_items.items(), 1):
            print(f"{Colors.YELLOW}{i}. {slot.capitalize()}: {Colors.BRIGHT_CYAN}{item.name}{Colors.RESET}")

        try:
            choice = int(input(f"\n{Colors.CYAN}Enter the number of the item to unequip (0 to cancel): {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(equipped_items):
                slot_to_unequip = list(equipped_items.keys())[choice - 1]
                self.unequip_item(slot_to_unequip)
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        except ValueError:
            print(f"\n{Colors.RED}Please enter a valid number.{Colors.RESET}")


    def update_total_armor(self):
        """Recalculates the player's total armor based on equipped items."""

        for slot, item in self.equipment.slots.items():
            if item and hasattr(item, "defense"):  # Vérifie si l'item a une stat de défense
                self.total_armor += item.defense

        for slot in self.equipment.__dict__.items():
            item = self.equipment.slots[slot]
            if item and hasattr(item, "effects"):
                for effect, value in item.effects.items():
                    setattr(self.stats, effect, getattr(self.stats, effect, 0) + value)

        self.update_stats_with_bonus()


    def calculate_set_bonus(self):
        """Calcule et applique les bonus de set en fonction des pièces d'armure équipées."""

        equipped_pieces = {}  # Dictionnaire pour compter les pièces équipées par set

        # Vérifie toutes les pièces d'armure équipées
        for slot in ["helmet", "chest", "gauntlets", "leggings", "boots"]:
            item = self.equipment.slots[slot]
            if item:
                armor_prefix = item.name.split()[0]
                if armor_prefix in armor_sets:
                    equipped_pieces[armor_prefix] = equipped_pieces.get(armor_prefix, 0) + 1

        self.set_bonuses.clear()

        # Applique les nouveaux bonus selon le nombre de pièces équipées
        for set_name, count in equipped_pieces.items():
            set_data = armor_sets[set_name]
            for threshold, bonus_name in sorted(set_data["bonus_thresholds"].items()):
                if count >= threshold:
                    self.set_bonuses[bonus_name] = set_data["effects"][bonus_name]

        self.update_stats_with_bonus()


    def update_stats_with_bonus(self):
        """Applies set bonuses to player stats."""
        
        # Reset les stats à leurs valeurs de base
        self.stats.remove_temporary_effects()

        # Applique les bonus de set
        for bonus_name, effects in self.set_bonuses.items():
            for stat, value in effects.items():
                if stat in self.stats.__dict__:
                    self.stats.__dict__[stat] += value  # Applique les bonus
                else:
                    print(f"{Colors.RED}Stat {stat} does not exist in player stats!{Colors.RESET}")
        self.stats.update_total_stats()


    def total_domage(self, base_damage=True):
        base_damage = self.stats.attack
        damage_main = getattr(self.equipment.main_hand, "damage", 0) or 0
        damage_off = getattr(self.equipment.off_hand, "damage", 0) or 0
        total_domage = 0

        if base_damage:
            if self.equipment.main_hand and self.equipment.off_hand:
                total_domage = base_damage + (damage_main + damage_off) // 1.5  # Réduction pour équilibrer
            else:
                total_domage = base_damage + damage_main + damage_off
        else:
            if self.equipment.main_hand and self.equipment.off_hand:
                total_domage = base_damage + (damage_main + damage_off) // 1.5  # Réduction pour équilibrer
            else:
                total_domage = base_damage + damage_main + damage_off
        return total_domage

    def level_up(self):
        self.level += 1
        self.stats.max_hp += 10
        self.stats.update_total_stats()
        self.stats.hp = self.stats.max_hp
        self.stats.attack += 2
        self.stats.defense += 1
        self.max_xp = int(self.max_xp * 1.5)
        self.stats.update_total_stats()
        
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}╔══════════════════════════════╗")
        print(f"║     LEVEL UP! Level {self.level}!     ║")
        print(f"╚══════════════════════════════╝{Colors.RESET}")
        print(f"{Colors.GREEN}Max HP +10 (Now {self.stats.max_hp})")
        print(f"Attack +2 (Now {self.stats.attack})")
        print(f"Defense +1 (Now {self.stats.defense}){Colors.RESET}")
        
        if self.level == 5:
            self.choose_class1()
        elif self.level == 10:
            self.choose_class2()

        if self.dungeon_level >= 10 and self.difficulty == "normal":
            self.unlocked_difficulties["soul_enjoyer"] = True
            self.unlocked_difficulties["realistic"] = True
            print(f"{Colors.BRIGHT_YELLOW}You have completed Normal mode! New difficulties unlocked!{Colors.RESET}")

    def choose_class1(self):
        clear_screen()
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}╔══════════════════════════════════════════╗")
        print(f"║     CLASS SPECIALIZATION AVAILABLE!     ║")
        print(f"╚══════════════════════════════════════════╝{Colors.RESET}")
        
        classes = {
            "1": {"name": "Warrior", "hp": 30, "attack": 5, "defense": 8, "agility": 3, "skill": "Berserk Rage"},
            "2": {"name": "Rogue", "hp": 15, "attack": 8, "defense": 3, "agility": 8, "skill": "Shadow Strike"},
            "3": {"name": "Mage", "hp": 10, "attack": 10, "defense": 0, "agility": 2, "skill": "Arcane Blast"},
            "4": {"name": "Knight", "hp": 25, "attack": 3, "defense": 10, "agility": 5, "skill": "Divine Shield"}
        }
        
        for key, cls_data in classes.items():
            print(f"\n{Colors.CYAN}[{key}] {cls_data['name']}{Colors.RESET}")
            print(f"  {Colors.GREEN}+{cls_data['hp']} Max HP{Colors.RESET}")
            print(f"  {Colors.RED}+{cls_data['attack']} Attack{Colors.RESET}")
            print(f"  {Colors.BLUE}+{cls_data['defense']} Defense{Colors.RESET}")
            print(f"  Skill: {Colors.MAGENTA}{cls_data['skill']}{Colors.RESET}")
        
        while True:
            choice = input(f"\n{Colors.YELLOW}Choose your class (1-4): {Colors.RESET}")
            if choice in classes:
                cls_data = classes[choice]
                self.class_name = cls_data["name"]
                self.stats.max_hp += cls_data["hp"]
                self.stats.hp = self.stats.max_hp
                self.stats.attack += cls_data["attack"]
                self.stats.defense += cls_data["defense"]
                # Ajout du Skill correspondant via le dictionnaire skills_dict
                skill_name = cls_data["skill"]
                if skill_name in skills_dict:
                    self.skills.append(skills_dict[skill_name])
                else:
                    print(f"{Colors.RED}Error: Skill {skill_name} not found.{Colors.RESET}")
                print(f"\n{Colors.BRIGHT_GREEN}You are now a {self.class_name}!{Colors.RESET}")
                print(f"You've learned the {Colors.MAGENTA}{cls_data['skill']}{Colors.RESET} skill!")
                input(f"\n{Colors.YELLOW}Press Enter to continue your adventure...{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and 4.{Colors.RESET}")


    def choose_class2(self):
        clear_screen()
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}╔══════════════════════════════════════════╗")
        print(f"║     CLASS SPECIALIZATION AVAILABLE!     ║")
        print(f"╚══════════════════════════════════════════╝{Colors.RESET}")
        
        classes = {
            "1": {"name": "Warrior", "hp": 30, "attack": 5, "defense": 8, "agility": 3, "skill": "Berserk Rage"},
            "2": {"name": "Rogue", "hp": 15, "attack": 8, "defense": 3, "agility": 8, "skill": "Shadow Strike"},
            "3": {"name": "Mage", "hp": 10, "attack": 10, "defense": 0, "agility": 2, "skill": "Arcane Blast"},
            "4": {"name": "Knight", "hp": 25, "attack": 3, "defense": 10, "agility": 5, "skill": "Divine Shield"}
        }
        
        for key, cls_data in classes.items():
            print(f"\n{Colors.CYAN}[{key}] {cls_data['name']}{Colors.RESET}")
            print(f"  {Colors.GREEN}+{cls_data['hp']} Max HP{Colors.RESET}")
            print(f"  {Colors.RED}+{cls_data['attack']} Attack{Colors.RESET}")
            print(f"  {Colors.BLUE}+{cls_data['defense']} Defense{Colors.RESET}")
            print(f"  Skill: {Colors.MAGENTA}{cls_data['skill']}{Colors.RESET}")
        
        while True:
            choice = input(f"\n{Colors.YELLOW}Choose your class (1-4): {Colors.RESET}")
            if choice in classes:
                cls_data = classes[choice]
                self.class_name = cls_data["name"]
                self.stats.max_hp += cls_data["hp"]
                self.stats.hp = self.stats.max_hp
                self.stats.attack += cls_data["attack"]
                self.stats.defense += cls_data["defense"]
                # Ajout du Skill correspondant via le dictionnaire skills_dict
                skill_name = cls_data["skill"]
                if skill_name in skills_dict:
                    self.skills.append(skills_dict[skill_name])
                else:
                    print(f"{Colors.RED}Error: Skill {skill_name} not found.{Colors.RESET}")
                print(f"\n{Colors.BRIGHT_GREEN}You are now a {self.class_name}!{Colors.RESET}")
                print(f"You've learned the {Colors.MAGENTA}{cls_data['skill']}{Colors.RESET} skill!")
                input(f"\n{Colors.YELLOW}Press Enter to continue your adventure...{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and 4.{Colors.RESET}")


    def gain_xp(self, amount):
        self.xp += amount
        print(f"{Colors.BRIGHT_GREEN}+{amount} XP{Colors.RESET}")
        
        # Check for level up
        if self.xp >= self.max_xp:
            excess = self.xp - self.max_xp
            self.xp = excess
            self.level_up()
            return True
        return False
    
    def use_skill(self, target):
        if not self.skills:
            print(f"{Colors.RED}You don't have any skills yet!{Colors.RESET}")
            return 0

        # Choisir le skill
        print(f"\n{Colors.YELLOW}Choose a skill to use:{Colors.RESET}")
        for i, skill in enumerate(self.skills, 1):
            print(f"{i}. {skill}")
        
        choice = input(f"\n{Colors.YELLOW}Enter the number of the skill to use: {Colors.RESET}")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(self.skills):
                skill = self.skills[choice - 1]
            else:
                print(f"{Colors.RED}Invalid skill choice.{Colors.RESET}")
                return 0
        else:
            print(f"{Colors.RED}Invalid input.{Colors.RESET}")
            return 0

        # Activation du skill
        multiplier = skill.activate(self)
        if multiplier == 0:
            # Si le coût n'est pas supporté, on n'active pas le skill
            return 0

        base_damage = self.total_domage()

        critical = random.random() < (0.05 + self.stats.luck * 0.01)
        if critical:
            base_damage *= 2
            print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}CRITICAL HIT!{Colors.RESET}")

        total_damage = int(base_damage * multiplier)
        damage, absorbed_damage = target.stats.take_damage(base_damage)
        total_damage = damage + absorbed_damage
        print(f"You deal {Colors.RED}{total_damage}{Colors.RESET} damage to {target.name}!")

        # Si le skill avait des bonus temporaires, il faudrait les retirer après l'attaque
        # On peut ici réinitialiser les stats en utilisant reset_base() si besoin
        # Par exemple, si le skill était Divine Shield, on pourrait remettre la défense à la base.
        # Pour ce cas, il faudrait que le skill gère lui-même le retrait du bonus après usage.

        return total_damage

    def display_dungeon_level(self, rooms_explored=0):
        # Display dungeon level and explored rooms
        print(f"\n{Colors.BRIGHT_BLUE}{Colors.BOLD}╔══════════════════════════════════╗")
        print(f"║   Dungeon Level: {self.dungeon_level}{' ' * (16 - len(str(self.dungeon_level)))}║")
        print(f"║   Rooms Explored: {rooms_explored}{' ' * (15 - len(str(rooms_explored)))}║")
        print(f"╚══════════════════════════════════╝{Colors.RESET}")

    def display_status(self):
        """Displays all player stats dynamically with proper formatting."""
        # Color mapping for stats
        stat_colors = {
            "hp": Colors.RED,
            "xp": Colors.BRIGHT_GREEN,
            "stamina": Colors.YELLOW,
            "mana": Colors.BRIGHT_BLUE,
            "max_hp": Colors.RED,
            "attack": Colors.BRIGHT_MAGENTA,
            "defense": Colors.BRIGHT_BLUE,
            "magic_damage": Colors.MAGENTA,
            "magic_defense": Colors.BLUE,
            "luck": Colors.BRIGHT_GREEN,
            "agility": Colors.BRIGHT_CYAN,
            "gold": Colors.BRIGHT_YELLOW,
            "souls": Colors.BRIGHT_BLACK,
            "critical_chance": Colors.BRIGHT_RED,
        }

        def truncate_text(text, length):
            """Truncate text to fit within the box width."""
            return text[:length] if len(text) > length else text.ljust(length)

        # Calculate bar lengths and ratios
        hp_ratio = self.stats.hp / self.stats.max_hp
        xp_ratio = self.xp / self.max_xp
        stamina_ratio = self.stats.stamina / self.stats.max_stamina
        mana_ratio = self.stats.mana / self.stats.max_mana

        def create_bar(ratio, length=46):
            """Create a progress bar based on ratio."""
            filled = int(length * ratio)
            return "█" * filled + "░" * (length - filled)


        # Prepare the box template
        box_len = 48
        def print_box_template():
            print(f"\n{Colors.YELLOW}╔═══════════════ {Colors.BOLD}CHARACTER STATUS{Colors.RESET}{Colors.YELLOW} ════════════════╗{Colors.RESET}")
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Character Name Placeholder
            print(f"{Colors.YELLOW}╠{'═' * (box_len + 1)}╣{Colors.RESET}")
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Level Placeholder
            # HP Section Placeholders
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # HP Text Placeholder
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # HP Bar Placeholder
            
            # XP Section Placeholders
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # XP Text Placeholder
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # XP Bar Placeholder
            
            # Stamina Section Placeholders
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Stamina Text Placeholder
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Stamina Bar Placeholder
            
            # Mana Section Placeholders
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Mana Text Placeholder
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Mana Bar Placeholder
            
            print(f"{Colors.YELLOW}╠{'═' * (box_len + 1)}╣{Colors.RESET}")
            
            # Gold and Souls Placeholders
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Gold Placeholder
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Souls Placeholder
            
            # Stats Placeholders
            for _ in range(8):
                print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")
            
            print(f"{Colors.YELLOW}╠{'═' * (box_len + 1)}╣{Colors.RESET}")
            
            # Equipment Placeholders
            for _ in range(12):
                print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")
            
            print(f"{Colors.YELLOW}╚{'═' * (box_len + 1)}╝{Colors.RESET}")

        # Clear screen and print box template
        print("\033[2J\033[H")  # Clear screen and move cursor to top
        print_box_template()

        # Move cursor back up to fill in the details (adding 1 for the initial newline)
        print("\033[37A")  # Move up to start of box (number of lines + 1)

        # Create empty line list and add content
        content_lines = []
        
        # Character Name
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_WHITE}{truncate_text(f'{self.name} the {self.class_name}', 46)}")
        
        # Skip separator line
        content_lines.append("")
        
        # Level
        content_lines.append(f"{Colors.YELLOW}║ {Colors.GREEN}{Colors.UNDERLINE}Level: {self.level}{Colors.RESET}".ljust(46))
        
        # HP
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['hp']}HP: {self.stats.hp}/{self.stats.max_hp}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['hp']}{create_bar(hp_ratio)}".ljust(46))
        
        # XP
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['xp']}XP: {self.xp}/{self.max_xp}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['xp']}{create_bar(xp_ratio)}".ljust(46))
        
        # Stamina
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['stamina']}Stamina: {self.stats.stamina}/{self.stats.max_stamina}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['stamina']}{create_bar(stamina_ratio)}".ljust(46))
        
        # Mana
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['mana']}Mana: {self.stats.mana}/{self.stats.max_mana}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['mana']}{create_bar(mana_ratio)}".ljust(46))
        
        # Skip separator line
        content_lines.append("")
        
        # Gold and Souls
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_YELLOW}Gold:{Colors.RESET} {self.gold}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_BLACK}Souls:{Colors.RESET} {self.souls}".ljust(46))

        # Skip separator line
        content_lines.append("")

        """
        # Additional Stats
        stat_count = 0
        for stat, base_value in self.stats.__dict__.items():
            if stat in ["base_stats", "permanent_stats", "hp", "max_hp", "max_stamina", "stamina", "max_mana", "mana", "equipment"]:
                continue
            if isinstance(base_value, dict):  
                continue

            color = stat_colors.get(stat, Colors.WHITE)
            stat_label = stat.replace("_", " ").capitalize()

            # Calculate equipment effects
            if stat == "attack":
                effects_value = 0
                if self.total_domage():
                    effects_value += self.total_domage(base_damage=False) - self.stats.attack
            elif stat == "defense":
                effects_value = sum(item.effects.get("defense", 0) if hasattr(item, "effects") else getattr(item, stat, 0)
                                for item in self.equipment.__dict__.values() if item)
            else:
                effects_value = sum(item.effects.get(stat, 0) if hasattr(item, "effects") else getattr(item, stat, 0)
                                for item in self.equipment.__dict__.values() if item)

            effects_text = f" (+{effects_value:>3})"
            line = f"{stat_label:<15}: {base_value:>3}{effects_text}"
            content_lines.append(f"{Colors.YELLOW}║ {color}{line}".ljust(46))
            stat_count += 1
        """

        # Additional Stats
        stat_count = 0
        for stat, base_value in self.stats.__dict__.items():
            if stat in ["base_stats", "permanent_stats", "hp", "max_hp", "max_stamina", "stamina", "max_mana", "mana", "equipment"]:
                continue
            if isinstance(base_value, dict):  
                continue

            color = stat_colors.get(stat, Colors.WHITE)
            stat_label = stat.replace("_", " ").capitalize()

            # Calculate equipment effects
            # equip_bonus = getattr(self.stats.equipment, stat, 0)
            equip_bonus = self.stats.equipment_bonuses.get(stat, 0)
            temp_bonus = self.stats.temporary_stats.get(stat, 0)
            total_bonus = equip_bonus + temp_bonus

            perm_value = self.stats.permanent_stats.get(stat, 0)
            
            effects_text = f" (+{equip_bonus:>3})" if total_bonus != 0 else ""
            line = f"{stat_label:<18}: {perm_value:>3}{effects_text}"
            content_lines.append(f"{Colors.YELLOW}║ {color}{line}".ljust(46))
            stat_count += 1

        # Skip separator line
        content_lines.append("")

        # Equipment
        for slot, item in self.equipment.slots.items():
            if item:
                item_name = item.name
                if isinstance(item, Weapon):
                    extra = f" ({stat_colors.get('attack', Colors.RESET)}{item.damage}{Colors.RESET})"
                elif isinstance(item, Armor):
                    defense_value = item.effects.get('defense', 0)
                    extra = f" ({stat_colors.get('defense', Colors.RESET)}{defense_value}{Colors.RESET})"
                elif isinstance(item, (Ring, Amulet, Belt)):
                    effects_str = ", ".join(f"{stat_colors.get(k, Colors.RESET)}{v}{Colors.RESET}" for k, v in item.effects.items())
                    extra = f" ({effects_str})"
                else:
                    extra = ""
                
                """
                # Traitement pour tout les items (soit weapon armor amulet ect on effect, soit weapon a damage, armor a defense, amulet a effect...)
                if item.effects:  # Vérifie si item.effects existe et n'est pas vide
                    effects_str = ", ".join(f"{stat_colors.get(k, Colors.RESET)}{v}{Colors.RESET}" for k, v in item.effects.items())
                    extra = f" ({effects_str})"
                else:
                    extra = ""
                """
                
                # Format with proper spacing
                item_display = f"{item_name:<20} {extra}"
                
                # Truncate if too long
                item_display = truncate_text(item_display, 46)
            else:
                item_display = "None"

            slot_line = f"{slot.capitalize():<10}: {item_display}"
            content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_CYAN}{slot_line}")

        # Skills
        skill_list = ", ".join(f"{skill.name} (Lv{skill.level})" for skill in self.skills) if self.skills else "None"
        content_lines.append(f"{Colors.YELLOW}║ {Colors.MAGENTA}Skills:{Colors.RESET} {truncate_text(skill_list, 39)}")

        # Add a blank line to end the box
        content_lines.append("")

        # Print content lines, skipping separator positions
        for i, line in enumerate(content_lines):
            print(f"\r{line}")

    def manage_inventory(self):
        """Handles inventory management: equip, use, unequip, or drop items dynamically."""

        if not self.inventory:
            print(f"\n{Colors.RED}Your inventory is empty!{Colors.RESET}")
            return
        
        managing = True
        while managing:
            print(f"\n{Colors.BRIGHT_CYAN}Your Inventory:{Colors.RESET}")

            # Trie l'inventaire (les objets équipés en premier, puis tri alphabétique)
            sorted_inventory = sorted(self.inventory, key=lambda item: (item not in self.equipment.__dict__.values(), item.name.lower()))

            for i, item in enumerate(sorted_inventory, 1):
                status = ""
                if item in self.equipment.__dict__.values():
                    status = f" {Colors.BRIGHT_RED}[EQUIPPED]{Colors.RESET}"
                print(f"{Colors.YELLOW}{i}. {str(item)}{status}{Colors.RESET}")
            
            print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
            print(f"{Colors.GREEN}U. Use/Equip Item{Colors.RESET}")
            print(f"{Colors.YELLOW}E. Unequip Item{Colors.RESET}")
            print(f"{Colors.RED}D. Drop Item{Colors.RESET}")
            print(f"{Colors.YELLOW}B. Back{Colors.RESET}")
            
            choice = input(f"\n{Colors.CYAN}What would you like to do? {Colors.RESET}").upper()
            
            if choice == "B":
                managing = False
            
            elif choice == "U":
                try:
                    item_index = int(input(f"\n{Colors.CYAN}Enter item number to use/equip: {Colors.RESET}")) - 1
                    if 0 <= item_index < len(sorted_inventory):
                        item = sorted_inventory[item_index]
                        
                        if isinstance(item, (Weapon, Armor, Ring, Amulet, Belt)):
                            self.equip_item(item)

                        elif isinstance(item, Potion):
                            item.use(self)

                        else:
                            print(f"\n{Colors.YELLOW}You can't use this item right now.{Colors.RESET}")
                    
                    else:
                        print(f"\n{Colors.RED}Invalid item number.{Colors.RESET}")

                except ValueError:
                    print(f"\n{Colors.RED}Please enter a valid number.{Colors.RESET}")

            elif choice == "E":
                self.unequip_item_menu()

            elif choice == "D":
                try:
                    item_index = int(input(f"\n{Colors.CYAN}Enter item number to drop: {Colors.RESET}")) - 1
                    if 0 <= item_index < len(sorted_inventory):
                        item = sorted_inventory[item_index]
                        
                        equipped_slot = None
                        for slot, equipped_item in self.equipment.__dict__.items():
                            if equipped_item == item:
                                equipped_slot = slot
                                break

                        if equipped_slot:
                            confirm = input(f"\n{Colors.RED}This item is equipped. Are you sure you want to drop it? (y/n) {Colors.RESET}").lower()
                            if confirm != "y":
                                continue
                            self.equipment.unequip(equipped_slot, self)

                        self.inventory.remove(item)
                        print(f"\n{Colors.YELLOW}You dropped {item.name}.{Colors.RESET}")

                    else:
                        print(f"\n{Colors.RED}Invalid item number.{Colors.RESET}")

                except ValueError:
                    print(f"\n{Colors.RED}Please enter a valid number.{Colors.RESET}")

            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")


    def view_quests(self):
        if not self.quests and not self.completed_quests:
            print(f"\n{Colors.YELLOW}You don't have any quests at the moment.{Colors.RESET}")
            return
        
        print(f"\n{Colors.BRIGHT_MAGENTA}Active Quests:{Colors.RESET}")
        if self.quests:
            for i, quest in enumerate(self.quests, 1):
                print(f"{Colors.YELLOW}{i}. {quest}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No active quests.{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_GREEN}Completed Quests:{Colors.RESET}")
        if self.completed_quests:
            for i, quest in enumerate(self.completed_quests, 1):
                print(f"{Colors.GREEN}{i}. {quest.title}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}No completed quests.{Colors.RESET}")
        
        # Check for completable quests
        completable = [q for q in self.quests if q.completed]
        if completable:
            print(f"\n{Colors.BRIGHT_YELLOW}You can turn in the following quests:{Colors.RESET}")
            for i, quest in enumerate(completable, 1):
                print(f"{Colors.YELLOW}{i}. {quest.title}{Colors.RESET}")
            
            try:
                choice = input(f"\n{Colors.CYAN}Enter quest number to turn in (0 to cancel): {Colors.RESET}")
                if choice.isdigit() and 1 <= int(choice) <= len(completable):
                    quest = completable[int(choice) - 1]
                    self.complete_quest(player, quest)
            except ValueError:
                pass
        input('Enter to continue...')
    
    def display_quests(self):
        """Display the player's active and completed quests"""
        clear_screen()
        print(f"\n{Colors.YELLOW}{Colors.BOLD}╔════════════════════ QUESTS ═════════════════════╗{Colors.RESET}")
        
        if not self.quests and not self.completed_quests:
            print(f"║ {Colors.YELLOW}{Colors.RED}You don't have any quests.{' ' * 22}║{Colors.RESET}")
        else:
            # Active quests
            if self.quests:
                print(f"║ {Colors.YELLOW}{Colors.CYAN}Active Quests:{' ' * 30}║{Colors.RESET}")
                for i, quest in enumerate(self.quests, 1):
                    quest_title = f"{i}. {quest.title} ({quest.current_progress}/{quest.objective_amount})"
                    if len(quest_title) > 45:
                        quest_title = quest_title[:42] + "..."
                    print(f"{Colors.YELLOW}║ {Colors.CYAN}{quest_title}{' ' * (45 - len(quest_title))}║{Colors.RESET}")
                    
                    quest_desc = f"   {quest.description}"
                    if len(quest_desc) > 45:
                        quest_desc = quest_desc[:42] + "..."
                    print(f"{Colors.YELLOW}║ {Colors.WHITE}{quest_desc}{' ' * (45 - len(quest_desc))}║{Colors.RESET}")
            
            # Completed quests
            if self.completed_quests:
                print(f"{Colors.YELLOW}║ {Colors.GREEN}Completed Quests:{' ' * 27}║{Colors.RESET}")
                for i, quest in enumerate(self.completed_quests, 1):
                    quest_title = f"{i}. {quest.title}"
                    if len(quest_title) > 45:
                        quest_title = quest_title[:42] + "..."
                    print(f"{Colors.YELLOW}║ {Colors.GREEN}{quest_title}{' ' * (45 - len(quest_title))}║{Colors.RESET}")
        
        print(f"{Colors.YELLOW}╚═══════════════════════════════════════════════════╝{Colors.RESET}")
        
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

    
    def complete_quest(self, player, quest):
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Complete: {quest.title}!{Colors.RESET}")
        print(f"{Colors.YELLOW}Rewards:{Colors.RESET}")
        print(f"{Colors.YELLOW}+ {quest.reward_gold} Gold{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}+ {quest.reward_xp} XP{Colors.RESET}")
        
        self.gold += quest.reward_gold
        self.gain_xp(quest.reward_xp)
        
        if quest.reward_item:
            print(f"{Colors.GREEN}+ {quest.reward_item.name}{Colors.RESET}")
            self.inventory.append(quest.reward_item)
        
        self.quests.remove(quest)
        self.completed_quests.append(quest)
    

    def save_player(self, filename="player_save.json"):
        """Saves the player's data to a JSON file.""" 
        if not filename.endswith('.json'):
            filename += '.json'

        # Ensure saves directory exists
        save_dir = "saves"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filepath = os.path.join(save_dir, filename)

        data = self.to_dict()

        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

        print(f"{Colors.GREEN}Game saved successfully!{Colors.RESET}")

    def to_dict(self):
        """Convert the Player object to a dictionary for serialization using a generic serializer."""
        def serialize_obj(obj):
            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, list):
                return [serialize_obj(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: serialize_obj(value) for key, value in obj.items()}
            elif hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
                # Call to_dict once and serialize the resulting dict without recursion on to_dict again
                dict_obj = obj.to_dict()
                if dict_obj is obj:
                    # Defensive: if to_dict returns self, avoid infinite recursion
                    return str(obj)
                return serialize_obj(dict_obj)
            elif hasattr(obj, "__dict__"):
                return {key: serialize_obj(value) for key, value in obj.__dict__.items()}
            else:
                return str(obj)  # fallback to string representation

        return serialize_obj(self)

    @classmethod
    def from_dict(cls, data):
        """Create a Player object from a dictionary."""
        player = cls(data["name"], data.get("difficulty", "normal"))
        player.level = data.get("level", 1)
        player.xp = data.get("xp", 0)
        player.max_xp = data.get("max_xp", 100)
        player.gold = data.get("gold", 0)

        # Load stats
        player.stats.__dict__.update(data.get("stats", {}))

        # Load inventory
        player.inventory = [Item.from_dict(item) for item in data.get("inventory", [])]

        # Load equipment
        eq_data = data.get("equipment", {})
        if eq_data:
            from items import Equipment
            player.equipment = Equipment.from_dict(eq_data)
        else:
            player.equipment = None

        player.total_armor = data.get("total_armor", 0)

        # Load skills
        from entity import Skill
        player.skills = [Skill(**skill) for skill in data.get("skills", [])]

        player.class_name = data.get("class_name", "Novice")
        player.dungeon_level = data.get("dungeon_level", 1)
        player.profession = data.get("profession", None)

        # Load quests
        from quests import Quest
        player.quests = [Quest.from_dict(quest) for quest in data.get("quests", [])]
        player.completed_quests = [Quest.from_dict(quest) for quest in data.get("completed_quests", [])]

        player.kills = data.get("kills", 0)
        player.difficulty = data.get("difficulty", "normal")
        player.unlocked_difficulties = data.get("unlocked_difficulties", {"normal": True, "soul_enjoyer": False, "realistic": False})
        player.finished_difficulties = data.get("finished_difficulties", {"normal": False, "soul_enjoyer": False, "realistic": False})

        return player


def load_player(filename=None):
    """Loads the player's data from a JSON file and reconstructs objects."""
    global debug
    debug = 0

    if filename is None:
        filename = "player_save.json"
        if debug >= 1:
            print(f"{Colors.BLUE}INFO: default filename set: {filename}{Colors.RESET}")

    # Ensure filename is in saves directory
    save_dir = "saves"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = os.path.join(save_dir, filename)

    if debug >= 1:
        print(f"{Colors.BLUE}INFO: filename: {filename}{Colors.RESET}")

    try:
        with open(filename, "r") as file:
            data = json.load(file)
            if debug >= 1:
                print(f"{Colors.BLUE}INFO: loaded data: {data}{Colors.RESET}")

        # Use from_dict to create player
        from entity import Player
        player = Player.from_dict(data)

        print(f"{Colors.GREEN}Game loaded successfully!{Colors.RESET}")
        return player

    except FileNotFoundError:
        print(f"{Colors.RED}No save file found! Starting a new game...{Colors.RESET}")
        handle_error()
        return Player()

    except KeyError as e:
        print(f"{Colors.RED}Error loading save file: Missing key{Colors.RESET}")
        handle_error()
        return Player()


def load_player(filename=None):
    """Loads the player's data from a JSON file and reconstructs objects."""
    global debug
    debug = 0

    if filename is None:
        filename = "player_save.json"
        if debug >= 1:
            print(f"{Colors.BLUE}INFO: default filename set: {filename}{Colors.RESET}")

    # Ensure filename is in saves directory
    save_dir = "saves"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = os.path.join(save_dir, filename)
    
    if debug >= 1:
        print(f"{Colors.BLUE}INFO: filename: {filename}{Colors.RESET}")
    
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            if debug >= 1:
                print(f"{Colors.BLUE}INFO: loaded data: {data}{Colors.RESET}")

        # Création du joueur avec les données chargées
        player = Player(data["name"], data["difficulty"])
        player.level = data["level"]
        player.xp = data["xp"]
        player.max_xp = data["max_xp"]
        player.gold = data["gold"]

        # Chargement des stats
        player.stats.__dict__.update(data["stats"])

        # Chargement de l'inventaire (conversion des dictionnaires en objets Item)
        player.inventory = [Item.from_dict(item) for item in data["inventory"]]

        # Chargement de l'équipement
        eq_data = {slot: Item.from_dict(item) if item else None for slot, item in data["equipment"].items()}
        if debug >= 1:
            print(f"DEBUG: eq_data before assignment -> {eq_data}")
            input()
        player.equipment = Equipment(**eq_data)
        player.total_armor = data["total_armor"]

        # Vérification et conversion des équipements en objets Gear si nécessaire
        if isinstance(player.equipment, dict):  
            player.equipment = Equipment(**{
                slot: Gear(**item) if isinstance(item, dict) else item
                for slot, item in player.equipment.items()
            })
        
        if debug >= 1:
            print(f"{Colors.BLUE}player.equipment: {player.equipment}{Colors.RESET}")


        player.skills = [Skill(**skill) for skill in data["skills"]]

        player.class_name = data["class_name"]
        player.dungeon_level = data["dungeon_level"]
        player.profession = data["profession"]

        # Chargement des quêtes
        player.quests = [Quest.from_dict(quest) for quest in data["quests"]]
        player.completed_quests = [Quest.from_dict(quest) for quest in data["completed_quests"]]

        player.kills = data["kills"]
        player.unlocked_difficulties = data["unlocked_difficulties"]
        player.finished_difficulties = data["finished_difficulties"]

        print(f"{Colors.GREEN}Game loaded successfully!{Colors.RESET}")
        return player

    except FileNotFoundError:
        print(f"{Colors.RED}No save file found! Starting a new game...{Colors.RESET}")
        handle_error()
        return Player()

    except KeyError as e:
        print(f"{Colors.RED}Error loading save file: Missing key{Colors.RESET}")
        handle_error()
        return Player()


def continue_game(filename):
    """Loads a saved game from a file."""
    try:
        player = load_player(filename)
        print(f"{Colors.GREEN}Welcome back, {player.name}!{Colors.RESET}")
        return player
    except Exception as e:
        print(f"{Colors.RED}Error loading saved game: {e}{Colors.RESET}")
        return None




class Enemy(Entity):
    """
    Represents an enemy character that the player can fight.

    Inherits from:
        Entity (Base class for all characters)

    Attributes:
        xp_reward (int): The XP granted upon defeating the enemy.
        gold_reward (int): The amount of gold dropped by the enemy.
        difficulty (int): A numerical scale from 1 to 10 determining enemy strength.

    Methods:
        attack_player(player: Player) -> int:
            Attacks the player and returns the damage dealt.
    """
    def __init__(self, name, enemy_type, hp, attack, defense, xp_reward, gold_reward, difficulty):
        super().__init__(name, hp, hp, attack, defense)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.difficulty = difficulty  # 1-10 scale
        self.type = enemy_type
    
    def attack_player(self, player):
        """Enemy attacks the player, considering total armor defense."""
        global debug

        # player.update_total_armor()
        damage = max(1, self.stats.attack - (player.stats.defense + player.total_armor))
        
        if debug >= 1:
            print('DEBUG: player hp:', player.stats.hp)
            
        player.stats.take_damage(damage)

        print(f"{self.name} attacks you for {Colors.RED}{damage}{Colors.RESET} damage!")
        
        if debug >= 1:
            print("DEBUG: player hp after attack:", player.stats.hp)

        return damage


def generate_enemy(level=1, is_boss=False):
    """Génère un ennemi ou un boss en fonction du niveau donné."""
    
    # Sélection des ennemis ou des boss disponibles pour ce niveau
    if is_boss:
        valid_types = [e for e in boss_types if e["min_level"] == level]
    else:
        valid_types = [e for e in enemy_types if e["min_level"] <= level]

    # Si aucun ennemi valide, on prend le premier ennemi par défaut
    if not valid_types:
        valid_types = [enemy_types[0]]

    # Sélection aléatoire d'un ennemi approprié
    enemy_data = random.choice(valid_types)

    # Définition des stats de base
    base_hp = 20 + level * 10
    base_attack = 10 + level * 2
    base_defense = 2 + level

    # Application des modificateurs de l'ennemi
    hp = int(base_hp * enemy_data["hp_mod"])
    attack = int(base_attack * enemy_data["atk_mod"])
    defense = int(base_defense * enemy_data["def_mod"])

    # Multiplier les stats si c'est un boss
    if is_boss:
        hp *= 2
        attack = int(attack * 1.5)
        defense = int(defense * 1.5)

    # Calcul des récompenses
    xp_reward = int(10 * level * (2 if is_boss else 1))
    gold_reward = int(5 * level * (3 if is_boss else 1))

    # Définition de la difficulté
    difficulty = level + (3 if is_boss else 0)

    # Formatage du nom (différent pour les boss)
    name = f"{Colors.RED}{enemy_data['name']}{Colors.RESET}"
    if is_boss:
        name = f"{Colors.BRIGHT_RED}{Colors.BOLD}{enemy_data['name']}{Colors.RESET}"

    # Création de l'objet Enemy avec le type correspondant
    return Enemy(name, enemy_data["type"], hp, attack, defense, xp_reward, gold_reward, difficulty)


if __name__ == '__main__':
    player = Player(name="Adventurer")
    enemy = Enemy(name="Goblin", hp=50, attack=10, defense=5, xp_reward=20, gold_reward=10, difficulty=5)
    
    print('enemy_test:', enemy)
    print('player_test:', player)
    player.display_status()
