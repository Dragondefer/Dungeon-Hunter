__version__ = "2460.0"
__creation__ = "09-03-2025"

# Dungeon Hunter - (c) Dragondefer 2025
# Licensed under CC BY-NC 4.0


# This file contains the core entity classes for the Dungeon Hunter game.
# Entities include players, enemies, and their stats, skills, and interactions.

# Modifications here affect gameplay mechanics deeply. Proceed with caution.
# Note: If you want to add things, try to copy what's already there and adapt it.

import random
import time
import json
import os
import shutil
import uuid
from typing import Type

import config
if config.DEV_AGENT_MODE:
    try:
        from ai.reward_engine import try_reward
        from ai.agent_wrapper import agent_is_enabled
    except ImportError: pass

from interface.colors import Colors
from engine.game_utility import (clear_screen, handle_error, typewriter_effect,
                          glitch_text, random_glitch_text, ancient_text,
                          glitch_burst, timed_input_pattern, strip_ansi,
                          get_input)
from items.items import (Item, Equipment, Gear, Weapon, Armor,
                   Ring, Amulet, Belt, Potion)
# Removed top-level import of data to fix circular import
# from data import armor_sets, enemy_types, boss_types, achievements, skills_dict, can_send_analytics
from items.inventory import Inventory
from core.spells import Spell, Scroll
from core.masteries import Mastery
from core.skills import Skill
from core.player_class import PlayerClass
from core.status_effects import StatusEffect
from items.items import Equipment

debug = 0

class StatContainer: # Pas utilsé
    """Classe pour gérer les stats permanentes et temporaires avec accès en notation pointée."""
    def __init__(self, base_stats):
        self.__dict__.update({key: 0 for key in base_stats})
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __repr__(self):
        return str(self.__dict__)


#̶̼͝ T̸̻̈́h̵̤͒ë̵͕́ s̸̱̅h̵̤͒ä̷̪́ď̶̙o̶͙͝ẅ̷̙́s̸̱̅ m̴̛̠ä̷̪́n̸̻̈́i̴̊͜p̵̦̆ŭ̵͇l̷̫̈́ä̷̪́ẗ̴̗́ë̵͕́ ÿ̸̡́o̶͙͝ŭ̵͇r̷͍̈́ v̶̼͝ë̵͕́r̷͍̈́ÿ̸̡́ ë̵͕́s̸̱̅s̸̱̅ë̵͕́n̸̻̈́c̴̱͝ë̵͕́.̵͇̆.̵͇̆.̵͇̆
class Stats:
    """Gère les stats du joueur avec des effets permanents et temporaires."""
    def __init__(self, **kwargs):
        """Initialisation des stats avec gestion des erreurs."""
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
                self.permanent_stats[key] = int(value)  # Assure que seules les valeurs valides sont appliquées


        # Initialisation des stats temporaires
        self.temporary_stats = {key: 0 for key in self.permanent_stats}
        self.equipment_stats = {key: 0 for key in self.permanent_stats}


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


    def __repr__(self):
        """Affiche les stats avec permanent, temporaire et équipement."""
        # Affichage structuré
        return (
            f"Permanent: {self.permanent_stats}\n"
            f"Temporary: {self.temporary_stats}\n"
            f"Equipment: {self.equipment_stats}\n"
        )

    
    def __getattr__(self, key):
        """Permet d'accéder directement à la valeur combinée des stats permanentes et temporaires."""
        if key in self.permanent_stats:
            return self.permanent_stats[key] + self.temporary_stats.get(key, 0)
        raise AttributeError(f"'Stats' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        """Si on modifie une stat existante, elle est ajoutée aux stats permanentes."""
        if "permanent_stats" in self.__dict__ and key in self.permanent_stats:
            self.permanent_stats[key] = int(value)  # Modifie directement les stats permanentes
        else:
            super().__setattr__(key, value)  # Utilisation normale pour les autres attributs


    def update_total_stats(self):
        """Met à jour les stats visibles en combinant permanent, temporaire et équipement."""
        global debug

        # Vérifie les dictionnaires
        if not isinstance(self.permanent_stats, dict):
            print(f"{Colors.RED}ERROR: permanent_stats is corrupted! Resetting...{Colors.RESET}")
            self.permanent_stats = {
                "hp": 100, "max_hp": 100, "attack": 10, "defense": 5,
                "magic_damage": 1, "magic_defense": 1, "agility": 5, "luck": 5,
                "mana": 20, "max_mana": 20, "stamina": 50, "max_stamina": 50,
                "critical_chance": 5
            }

        if not isinstance(self.temporary_stats, dict):
            print(f"{Colors.RED}ERROR: temporary_stats is corrupted! Resetting...{Colors.RESET}")
            self.temporary_stats = {key: 0 for key in self.permanent_stats}

        if not isinstance(self.equipment_stats, dict):
            print(f"{Colors.RED}ERROR: equipment_stats is corrupted! Resetting...{Colors.RESET}")
            self.equipment_stats = {key: 0 for key in self.permanent_stats}

        # Vérifie les types des valeurs
        for key in self.permanent_stats:
            if not isinstance(self.permanent_stats[key], (int, float)):
                print(f"{Colors.RED}ERROR: permanent_stats[{key}] invalid. Reset to 0.{Colors.RESET}")
                self.permanent_stats[key] = 0
            if not isinstance(self.temporary_stats.get(key, 0), (int, float)):
                print(f"{Colors.RED}ERROR: temporary_stats[{key}] invalid. Reset to 0.{Colors.RESET}")
                self.temporary_stats[key] = 0
            if not isinstance(self.equipment_stats.get(key, 0), (int, float)):
                print(f"{Colors.RED}ERROR: equipment_stats[{key}] invalid. Reset to 0.{Colors.RESET}")
                self.equipment_stats[key] = 0

        # Mise à jour des stats totales
        self.total_stats = {
            key: self.permanent_stats.get(key, 0)
                + self.temporary_stats.get(key, 0)
                + self.equipment_stats.get(key, 0)
            for key in self.permanent_stats
        }

        # Injection dans self pour accès direct
        self.__dict__.update(self.total_stats)

        if debug >= 1:
            print(f"{Colors.CYAN}DEBUG: Total Stats Calculated -> {self.total_stats}{Colors.RESET}")
            print(f"{Colors.YELLOW}DEBUG: Equipment Stats -> {self.equipment_stats}{Colors.RESET}")
            input()

    def modify_stat(self, stat_name, value, stat_type="permanent"):
        """
        Modifie une stat de façon permanente, temporaire ou équipement.
        :param stat_name: Nom de la stat à modifier.
        :param value: Valeur à ajouter ou soustraire.
        :param stat_type: Type de stat à modifier ("permanent", "temporary", "equipment").
        """
        global debug
        if stat_type == "permanent":
            if stat_name in self.permanent_stats:
                self.permanent_stats[stat_name] += value
            else:
                print(f"{Colors.RED}Stat {stat_name} does not exist in permanent stats!{Colors.RESET}")
                return
        elif stat_type == "temporary":
            if stat_name in self.temporary_stats:
                self.temporary_stats[stat_name] += value
            else:
                print(f"{Colors.RED}Stat {stat_name} does not exist in temporary stats!{Colors.RESET}")
                return
        elif stat_type == "equipment":
            if stat_name in self.equipment_stats:
                self.equipment_stats[stat_name] += value
            else:
                print(f"{Colors.RED}Stat {stat_name} does not exist in equipment stats!{Colors.RESET}")
                return
        else:
            print(f"{Colors.RED}Invalid stat_type '{stat_type}'! Must be 'permanent', 'temporary', or 'equipment'.{Colors.RESET}")
            return
        
        # Mise à jour des stats visibles
        self.update_total_stats()

        if config.DEV_AGENT_MODE: try_reward(value)

        if debug >= 1:
            print(f"{Colors.GREEN}{stat_name.capitalize()} changed by {value} in {stat_type}! (Now {self.__dict__.get(stat_name, 'N/A')}){Colors.RESET}")

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

    def reset_equipment_stats(self):
        self.equipment_stats = {key: 0 for key in self.permanent_stats}

    def take_damage(self, damage:int|float):
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
            self.temporary_stats["hp"] -= int(damage_absorbed)
            damage -= damage_absorbed  # Mise à jour des dégâts restants
        else:
            damage_absorbed = 0

        # S'il reste des dégâts, ils sont appliqués aux HP permanents
        if damage > 0:
            self.permanent_stats["hp"] = int(max(0, hp_perm - damage))

        # Mise à jour des HP affichés (permanents + temporaires)
        self.update_total_stats()

        if debug >= 1:
            print(f"DEBUG: After damage -> Temp HP: {self.temporary_stats['hp']}/{hp_max_temp},\n"
                f"Perm HP: {self.permanent_stats['hp']}/{self.permanent_stats['max_hp']}")
        
        # return total damage
        return damage, damage_absorbed



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

        self.status_effects: list[StatusEffect] = []  # liste d'effets actifs

        # <0: vulnérabilité ; >0: résistance
        self.resistances = {
            "poison": 0,
            "burn": 0,
            "freeze": 0
            }

    
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
    

    def process_status_effects(self):
        for effect in self.status_effects[:]:
            effect.on_turn_start(self)
            if effect.is_expired():
                print(f"{self.name} is no longer affected by {effect.name}.")
                self.status_effects.remove(effect)
    
    def try_apply_status(self, effect: StatusEffect | str):
        from .status_effects import EFFECT_MAP
        if not isinstance(effect, StatusEffect) and isinstance(effect, str):
            if effect in EFFECT_MAP:
                try:
                    effect = EFFECT_MAP[effect]()
                except TypeError as e:
                    print(f"Error: cannot instantiate effect '{effect}' from EFFECT_MAP: {e}")
                    return
            else:
                print(f"Error: trying to apply effect: {effect}\nbut it isn't a StatusEffect instance and not in EFFECT_MAP")
                return

        resistance = self.resistances.get(effect.name.lower(), 0)
        if random.randint(0, 100) < (100 - resistance):
            # Check if effect of same name already exists
            existing_effect = next((e for e in self.status_effects if e.name == effect.name), None)
            if existing_effect:
                # Refresh or extend duration
                existing_effect.duration = max(existing_effect.duration, effect.duration)
                print(f"{self.name}'s {effect.name} effect duration refreshed.")
            else:
                self.status_effects.append(effect)
                effect.apply(self)
                print(f"{self.name} is affected by {effect.name}.")
        else:
            print(f"{self.name} resisted {effect.name}.")


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


#̶̼͝ T̸̻̈́h̵̤͒ë̵͕́ p̵̦̆l̷̫̈́ä̷̪́ÿ̸̡́ë̵͕́r̷͍̈́’s̸̱̅ f̷̠͑ä̷̪́ẗ̴̗́ë̵͕́ i̴̊͜s̸̱̅ ẅ̷̙́r̷͍̈́i̴̊͜ẗ̴̗́ẗ̴̗́ë̵͕́n̸̻̈́ i̴̊͜n̸̻̈́ b̸̼̅l̷̫̈́o̶͙͝o̶͙͝ď̶̙ ä̷̪́n̸̻̈́ď̶̙ c̴̱͝o̶͙͝ď̶̙ë̵͕́.̵͇̆

from engine.difficulty import GameMode, NormalMode, RealisticMode

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

    def __init__(self, name="Adventurer", difficulty=GameMode()):
        """Initialise le joueur avec des stats de base et un équipement vide."""
        import uuid
        from engine.game_utility import get_or_create_user_id
        super().__init__(name, 100, 100, 5, 5)  # Héritage de la classe Entity

        import time
        self._playtime_start = time.time()  # Timestamp when playtime tracking starts
        self.playtime_seconds = 0  # Total accumulated playtime in seconds

        from engine.difficulty import GameMode, NormalMode, RealisticMode, SoulsEnjoyerMode

        if isinstance(difficulty, GameMode):
            self.mode = difficulty
        elif isinstance(difficulty, str):
            diff_lower = difficulty.lower()
            if diff_lower == "normal":
                self.mode = NormalMode()
            elif diff_lower == "realistic":
                self.mode = RealisticMode()
            elif diff_lower == "soul_enjoyer" or diff_lower == "souls_enjoyer":
                self.mode = SoulsEnjoyerMode()
            else:
                print(f"Unknown difficulty '{difficulty}', setting to NormalMode by default.")
                self.mode = NormalMode()
        else:
            print(f"Invalid difficulty type '{type(difficulty)}', setting to NormalMode by default.")
            self.mode = NormalMode()

        self.difficulty_data = {}

        self.level = 1
        self.xp = 0
        self.max_xp = 100
        self.gold = 50
        self.souls = 0
        self.sin = 0

        # Add user_id for persistent anonymous user identification
        self.user_id = get_or_create_user_id()

        # Add player_id for unique identification
        self.player_id = str(uuid.uuid4())

        self.deaths_per_room = {}
        self.levels_completed = 0
        self.total_deaths = 0
        self.total_play_sessions = 1

        # Équipement initialisé avant les stats (pour pouvoir l'envoyer dans Stats)
        self.equipment = Equipment(
            main_hand=None, off_hand=None, helmet=None, chest=None,
            gauntlets=None, leggings=None, boots=None, shield=None,
            ring=None, amulet=None, belt=None
        )

        # Add tutorial_completed attribute to track tutorial completion
        self.tutorial_completed = False

        # Création des stats en incluant l'équipement
        self.stats = Stats(hp=100, max_hp=100, attack=5, defense=5,
                           magic_damage=1, magic_defense=1, agility=5, luck=5,
                           mana=20, max_mana=20, stamina=50, max_stamina=50,
                           critical_chance=5)

        self.set_bonuses = {}
        self.displayed_set_bonuses = set()
        self.skills = []
        self.kills = 0

        self.critical_count = 0
        self.attack_count = 0


        self.class_name = "Novice"
        self.profession = None
        self.quests = []
        self.completed_quests = []
        from data import achievements
        self.achievements = achievements
        self.seen_events = set()

        self.tutorial_rooms_shown = {
            "combat_tutorial": False,
            "treasure_tutorial": False,
            "shop_tutorial": False,
            "puzzle_tutorial": False,
            "rest_tutorial": False,
            }


        self.dungeon_level = 1
        self.current_room_number = 0
        self.total_rooms_explored = 0
        self.position: tuple[int, int] = (0, 0)


        # New stats for tracking player activities
        self.shops_visited = 0
        self.combat_encounters = 0
        self.rest_rooms_visited = 0
        self.puzzles_solved = 0
        self.treasures_found = 0
        self.traps_triggered = 0
        self.bosses_defeated = 0
        self.items_collected = 0
        self.gold_spent = 0
        self.damage_dealt = 0
        self.damage_taken = 0

        # Analytics stats
        self.mostDeadlyEnemies = []  # List of enemy names for each death event
        self.combatSuccessByLevel = {}
        self.skillsUsageFrequency = {}
        self.roomTypePreferences = {}
        self.explorationDepthByDifficulty = {
            "Normal": 0,
            "Realistic": 0,
            "Souls Enjoyer": 0
        }
        self.puzzleSuccessRateOverTime = []
        self.bossEncounterOutcomes = {
            "Victory": 0,
            "Defeat": 0,
            "Fled": 0
        }
        self.goldSpendingPatterns = []
        self.equipmentUsageByType = {}
        self.shopVisitFrequency = {}
        self.purchased_items: dict[Item, int] = {}
        self.levelDistribution = {}
        self.classSpecializationChoices = {}
        self.xpGainOverTime = []
        self.achievementCompletionRates = []

        self.ng_plus = {"normal": 0, "soul_enjoyer": 0, "realistic": 0}

        self.unlocked_difficulties = {"normal": True, "soul_enjoyer": False, "realistic": False}
        self.finished_difficulties = {"normal": False, "soul_enjoyer": False, "realistic": False}

        self.inventory = Inventory(self)
        self.inventory.append(Potion("Minor Health Potion", "Restores some health", 100, "heal", 50))

        self.known_spells: list[Spell] = []
        self.masteries: dict[str, Mastery] = {}  # exemple : {"sword": Mastery("sword"), "fire_magic": Mastery("fire_magic")}


        # Met à jour les stats avec l'équipement initial (même s'il est vide)
        self.stats.update_total_stats()
        self.apply_all_equipment_effects()

    def increment_deaths_in_room(self, difficulty_name: str, room_id: int):
        """Increment the death count for a specific room under a difficulty."""
        if difficulty_name not in self.deaths_per_room:
            self.deaths_per_room[difficulty_name] = {}
        if room_id in self.deaths_per_room[difficulty_name]:
            self.deaths_per_room[difficulty_name][room_id] += 1
        else:
            self.deaths_per_room[difficulty_name][room_id] = 1
        self.total_deaths += 1

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def __repr__(self):
        attrs = vars(self)
        attr_strs = [f"{k}={v!r}" for k, v in attrs.items()]
        return f"<Player " + ", ".join(attr_strs) + ">"
    
    
    def get_playtime(self):
        """Return the total playtime in seconds including current session."""
        import time
        current_time = time.time()
        elapsed = current_time - self._playtime_start
        return self.playtime_seconds + elapsed

    def get_formatted_playtime(self):
        """Return the total playtime as a formatted string HH:MM:SS."""
        total_seconds = int(self.get_playtime())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    

    def increment_levels_completed(self):
        """Increment the count of levels completed."""
        self.levels_completed += 1

    def increment_play_sessions(self):
        """Increment the count of total play sessions."""
        self.total_play_sessions += 1

    def move_player(self, direction, dungeon_grid):
        if direction in dungeon_grid[player.position].connections:
            new_pos = dungeon_grid[player.position].connections[direction]
            if new_pos in dungeon_grid:
                self.position = new_pos
                return dungeon_grid[new_pos]
        return None  # Invalid move


    def get_mastery(self, key: str) -> Mastery:
        if key not in self.masteries:
            self.masteries[key] = Mastery(name=key)
        return self.masteries[key]

    def gain_mastery_xp(self, key: str, amount: int):
        self.get_mastery(key).gain_xp(amount)


    def display_logbook(self):
        """Display a logbook of every monster discovered with notes and other info."""
        clear_screen()
        print(f"\n{Colors.BRIGHT_MAGENTA}Monster Logbook (Placeholder){Colors.RESET}")
        print("This feature will display all monsters discovered with notes and other details.")
        input(f"\n{Colors.YELLOW}Press Enter to return...{Colors.RESET}")

    def display_skill_mastery(self):
        """Display XP and levels of each skill mastery."""
        clear_screen()
        print(f"\n{Colors.BRIGHT_CYAN}Skill Mastery (Placeholder){Colors.RESET}")
        if not self.skills:
            print("You have not acquired any skills yet.")
        else:
            for skill in self.skills:
                print(f"- {skill.name} (Level )")
        input(f"\n{Colors.YELLOW}Press Enter to return...{Colors.RESET}")


    def learn_spell(self, spell: Spell):
        """Add a spell to the player's known spells."""
        if spell not in self.known_spells:
            self.known_spells.append(spell)
            print(f"{Colors.GREEN}You have learned the spell: {spell.name}!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}You already know the spell: {spell.name}.{Colors.RESET}")

    def cast_spell(self, spell_name: str, target):
        """Cast a known spell by name on a target."""
        spell = next((s for s in self.known_spells if s.name.lower() == spell_name.lower()), None)
        if not spell:
            print(f"{Colors.RED}You don't know the spell '{spell_name}'.{Colors.RESET}")
            return False
        return spell.cast(self, target)

    def use_scroll(self, scroll: Scroll, target):
        """Use a scroll item to cast its spell."""
        if scroll in self.inventory:
            return scroll.use(self, target)
        else:
            print(f"{Colors.RED}You don't have the scroll '{scroll.name}' in your inventory.{Colors.RESET}")
            return False

    def save_difficulty_data(self):
        """Save current difficulty's inventory, gold, level, stats, and other relevant data."""
        diff_name = self.mode.name
        self.difficulty_data[diff_name] = {
            "inventory": [item.to_dict() for item in self.inventory],
            "gold": self.gold,
            "level": self.level,
            "xp": self.xp,
            "max_xp": self.max_xp,
            "stats": self.stats.permanent_stats.copy(),
            "equipment": self.equipment.to_dict() if self.equipment else None,
            "skills": [skill.to_dict() for skill in self.skills],
            "dungeon_level": self.dungeon_level,
            "class_name": self.class_name,
            # Add other per-difficulty data as needed
        }

    def load_difficulty_data(self, difficulty_name):
        """Load inventory, gold, level, stats, and other data for the given difficulty."""
        data = self.difficulty_data.get(difficulty_name)
        from items.items import Equipment
        
        if data:
            from items.items import Item
            from core.skills import Skill

            self.inventory.clear()
            for item_data in data["inventory"]:
                item = Item.from_dict(item_data)
                self.inventory.append(item)

            self.gold = data["gold"]
            self.level: int = data["level"]
            self.xp = data["xp"]
            self.max_xp = data["max_xp"]

            self.stats.permanent_stats.update(data["stats"])
            self.stats.update_total_stats()

            if data["equipment"]:
                self.equipment = Equipment.from_dict(data["equipment"])
                self.stats.equipment = self.equipment
            else:
                self.equipment = Equipment()
                self.stats.equipment = self.equipment

            self.skills = [Skill.from_dict(skill_data) for skill_data in data["skills"]]

            self.dungeon_level = data.get("dungeon_level", 1)
            self.class_name = data.get("class_name", "Novice")

        else:
            # Initialize default values for new difficulty
            self.inventory.clear()
            self.gold = 0
            self.level = 1
            self.xp = 0
            self.max_xp = 100
            self.stats.permanent_stats = {
                "hp": 100, "max_hp": 100,
                "attack": 5, "defense": 5,
                "magic_damage": 1, "magic_defense": 1,
                "agility": 5, "luck": 5,
                "mana": 20, "max_mana": 20,
                "stamina": 50, "max_stamina": 50,
                "critical_chance": 5
            }
            
            self.stats.update_total_stats()
            self.equipment = Equipment()
            self.stats.equipment = self.equipment
            self.skills = []
            self.dungeon_level = 1
            self.class_name = "Novice"

    def to_dict(self):
        data = self.__dict__.copy()

        # Nettoyage / conversions spécifiques
        data["equipment"] = self.equipment.to_dict() if self.equipment else None
        data["inventory"] = [item.to_dict() for item in self.inventory]
        data["skills"] = [skill.to_dict() for skill in self.skills]
        data["quests"] = [quest.to_dict() for quest in self.quests]
        data["completed_quests"] = [quest.to_dict() for quest in self.completed_quests]
        data["achievements"] = [ach.to_dict() for ach in self.achievements]
        data["stats"] = {k: v for k, v in self.stats.__dict__.items() if k != "equipment"}
        data["seen_events"] = list(self.seen_events)
        data["mode"] = self.mode.to_dict()
        data["displayed_set_bonuses"] = list(self.displayed_set_bonuses) if hasattr(self, "displayed_set_bonuses") else []
        data["status_effects"] = [effect.__dict__ for effect in self.status_effects] if self.status_effects else []
        data["masteries"] = {k: v.to_dict() for k, v in self.masteries.items()}

        # Convert player_class to dict if present
        if hasattr(self, "player_class") and self.player_class is not None:
            data["player_class"] = self.player_class.to_dict()
        else:
            data["player_class"] = None

        # Add playtime_seconds to saved data
        data["playtime_seconds"] = self.playtime_seconds

        # Add new stats to saved data
        data["player_id"] = self.player_id
        data["deaths_per_room"] = self.deaths_per_room
        data["levels_completed"] = self.levels_completed
        data["total_deaths"] = self.total_deaths
        data["total_play_sessions"] = self.total_play_sessions

        # Add analytics variables needed for analytics.html
        data["player_name"] = self.name
        data["level"] = self.level
        data["difficulty"] = self.mode.name if hasattr(self.mode, "name") else str(self.mode)
        data["rooms_explored"] = self.total_rooms_explored
        data["combat_encounters"] = self.combat_encounters
        data["damage_dealt"] = self.damage_dealt
        data["damage_taken"] = self.damage_taken
        data["gold_spent"] = self.gold_spent
        data["deaths"] = self.total_deaths

        # Fix for JSON serialization: convert purchased_items keys to strings
        data["purchased_items"] = {str(k): v for k, v in self.purchased_items.items()}

        return data

    @classmethod
    def from_dict(cls, data):
        from core.progression import Quest, Achievement
        from engine.difficulty import GameMode
        import time
        from core.player_class import PlayerClass

        player = cls(data.get("name", "Adventurer"), GameMode.from_dict(data.get("mode", {})))

        # Remplissage générique
        for key, value in data.items():
            if key in ("equipment", "inventory", "skills", "quests", "completed_quests", "achievements", "stats", "mode", "seen_events", "displayed_set_bonuses", "playtime_seconds", "player_id", "deaths_per_room", "levels_completed", "total_deaths", "total_play_sessions", "player_class"):
                continue  # On gère ceux-là à part
            setattr(player, key, value)

        # Champs complexes
        player.stats.__dict__.update(data.get("stats", {}))
        player.inventory = [Item.from_dict(i) for i in data.get("inventory", [])]
        player.equipment = Equipment.from_dict(data["equipment"]) if data.get("equipment") else None
        player.skills = [Skill.from_dict(s) for s in data.get("skills", [])]
        player.quests = [Quest.from_dict(q) for q in data.get("quests", [])]
        player.completed_quests = [Quest.from_dict(q) for q in data.get("completed_quests", [])]

        # Achievements avec condition_mapping
        condition_map = {ach.id: ach.condition for ach in player.achievements}
        player.achievements = [Achievement.from_dict(a, condition_map) for a in data.get("achievements", [])]

        player.seen_events = set(data.get("seen_events", []))
        player.displayed_set_bonuses = set(data.get("displayed_set_bonuses") or [])

        if player.equipment:
            player.apply_all_equipment_effects()
            
        from core.status_effects import status_effect_from_dict

        player.status_effects = [
            effect for effect in (status_effect_from_dict(e) for e in data.get("status_effects", [])) if effect
        ]

        player.masteries = {k: Mastery.from_dict(v) for k, v in data.get("masteries", {}).items()}

        # Restore playtime_seconds and reset _playtime_start to current time
        player.playtime_seconds = data.get("playtime_seconds", 0)
        player._playtime_start = time.time()

        # Restore new stats
        player.player_id = data.get("player_id", str(uuid.uuid4()))
        player.deaths_per_room = data.get("deaths_per_room", {})
        player.levels_completed = data.get("levels_completed", 0)
        player.total_deaths = data.get("total_deaths", 0)
        player.total_play_sessions = data.get("total_play_sessions", 1)

        # Restore player_class from dict if present
        player_class_data = data.get("player_class")
        if player_class_data:
            from core.player_class import PlayerClass
            player.player_class = PlayerClass.from_dict(player_class_data)
        else:
            player.player_class = None

        return player

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


    def equip_item(self, item):
        """Equip a weapon or armor piece in the correct slot automatically."""
        global debug

        if isinstance(item, Weapon):
            # Vérifier si l'arme est déjà équipée
            if item in [self.equipment.main_hand, self.equipment.off_hand]:
                print(f"\n{Colors.RED}You have already equipped {item.name}!{Colors.RESET}")
                return

            # Vérifier si une main est libre pour équiper l'arme
            if not self.equipment.main_hand:
                self.equipment.equip(slot="main_hand", item=item, player=self)
                print(f"\n{Colors.GREEN}You equipped {item.name} in your main hand!{Colors.RESET}")
            elif not self.equipment.off_hand:
                self.equipment.equip(slot="off_hand", item=item, player=self)
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
            elif isinstance(item, Armor):
                slot = armor_slot_map.get(item.armor_type) if isinstance(item.armor_type, str) else None  # Pour les armures classiques
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
                        print(f"\n{Colors.YELLOW}Did not equip {item.name}.{Colors.RESET}")
                else:
                    if debug >= 1:
                        print(f"Équipement avant: {self.equipment.slots}")  # Debug avant équipement
                    self.equipment.equip(slot, item, self)
                    if debug >= 1:
                        print(f"Équipement après: {self.equipment.slots}")  # Debug après équipement
                    print(f"\n{Colors.GREEN}You equipped {item.name} in {slot}!{Colors.RESET}")
                    self.inventory.remove(item)
            else:
                print(f"\n{Colors.RED}Invalid armor type: {getattr(item, 'armor_type', 'Unknown')}{Colors.RESET}")

        else:
            print(f"\n{Colors.YELLOW}You can't equip this item.{Colors.RESET}")

    def unequip_item(self, slot):
        """Déséquipe un objet (arme, armure, accessoire) et le remet dans l'inventaire."""
        if slot in self.equipment.slots and self.equipment.slots[slot]:
            item = self.equipment.unequip(slot, self)  # Utilise la méthode unequip de Equipment
            self.inventory.append(item)  # Remet l'objet dans l'inventaire
            if item is not None:
                print(f"\n{Colors.YELLOW}You unequipped {item.name} and placed it back in your inventory.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Error: Unequipped item is None.{Colors.RESET}")
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
            choice = int(get_input(f"\n{Colors.CYAN}Enter the number of the item to unequip (0 to cancel): {Colors.RESET}", options=[str(i) for i in range(len(equipped_items) + 1)], player=self))
            if choice == 0:
                return
            elif 1 <= choice <= len(equipped_items):
                slot_to_unequip = list(equipped_items.keys())[choice - 1]
                self.unequip_item(slot_to_unequip)
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        except ValueError:
            print(f"\n{Colors.RED}Please enter a valid number.{Colors.RESET}")


    def get_equipment_stats(self):
        global debug
        debug = 0

        total_stats = {}

        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Calculating equipment stats...{Colors.RESET}")

        for item in self.equipment.slots.values():
            if item:
                if debug >= 1:
                    print(f"{Colors.CYAN}DEBUG: Processing item: {item.name}{Colors.RESET}")
                if hasattr(item, "effects") and isinstance(item.effects, dict):
                    for stat, value in item.effects.items():
                        total_stats[stat] = total_stats.get(stat, 0) + value
                        if debug >= 1:
                            print(f"{Colors.CYAN}DEBUG: Adding {stat}: {value}{Colors.RESET}")

        if debug >= 1:
            print(f"{Colors.GREEN}DEBUG: Total equipment stats: {total_stats}{Colors.RESET}")

        return total_stats

    """
    def get_set_bonus_stats(self):
        global debug

        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Calculating set bonus stats...{Colors.RESET}")

        equipped_sets = {}

        for item in self.equipment.slots.values():
            if item and hasattr(item, "set_name"):
                equipped_sets[item.set_name] = equipped_sets.get(item.set_name, 0) + 1
                if debug >= 1:
                    print(f"{Colors.CYAN}DEBUG: Counting set {item.set_name}: {equipped_sets[item.set_name]}{Colors.RESET}")

        total_bonus = {}

        for set_name, count in equipped_sets.items():
            if set_name not in armor_sets:
                if debug >= 1:
                    print(f"{Colors.RED}DEBUG: Set {set_name} not found in armor_sets!{Colors.RESET}")
                continue
            set_data = armor_sets[set_name]
            for threshold, bonus_name in set_data["bonus_thresholds"].items():
                if count >= threshold:
                    bonus_effects = set_data["effects"][bonus_name]
                    for stat, value in bonus_effects.items():
                        total_bonus[stat] = total_bonus.get(stat, 0) + value
                        if debug >= 1:
                            print(f"{Colors.CYAN}DEBUG: Adding set bonus {stat}: {value} from {bonus_name}{Colors.RESET}")

        if debug >= 1:
            print(f"{Colors.GREEN}DEBUG: Total set bonus stats: {total_bonus}{Colors.RESET}")

        return total_bonus
    """


    def apply_all_equipment_effects(self, show_text=False):
        global debug
        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Recalculating equipment + set effects...{Colors.RESET}")

        # Reset anciens effets
        self.stats.remove_temporary_effects()
        self.stats.reset_equipment_stats()
        self.set_bonuses.clear()

        # Remove bonuses that are no longer active from displayed_set_bonuses
        current_active_bonuses = set()

        if debug >= 1:
            print(f"{Colors.CYAN}DEBUG: Cleared temporary effects and set bonuses.{Colors.RESET}")
            
        # Du​n​g​e​o​n ​H​u​nt​e​r​ ​- ​(​c​) D​r​a​g​on​d​e​fe​r​ ​2​0​25
        # L​i​ce​n​s​e​d​ ​un​d​e​r ​C​C​-​B​Y​-​NC​ ​4​.0
        # Dictionnaire cumulé des stats
        total_stats = {}

        # --- 1. Stats des items équipés ---
        for slot, item in self.equipment.slots.items():
            if item:
                if debug >= 1:
                    print(f"{Colors.CYAN}DEBUG: Processing item in slot {slot}: {item.name}{Colors.RESET}")
                # Effets d’objets (sous forme de dict)
                if hasattr(item, "effects"):
                    for stat, value in item.effects.items():
                        total_stats[stat] = total_stats.get(stat, 0) + value
                        if debug >= 1:
                            print(f"{Colors.GREEN}DEBUG: Adding effect {stat}: {value}{Colors.RESET}")

        # --- 2. Calcul des bonus de set ---
        equipped_sets = {}
        for slot in ["helmet", "chest", "gauntlets", "leggings", "boots"]:
            item = self.equipment.slots.get(slot)
            if item:
                from data.enemies_data import armor_sets
                # prefix = item.name.split()[1] # here, we assume the prefix is the second word in the name so it can be wrong as if it's in pos 1
                prefix = next((prefix for prefix in armor_sets if prefix in item.name), None)
                if debug >= 1:
                    print(f"{Colors.CYAN}DEBUG: Prefix: {prefix}{Colors.RESET}")
                if prefix in armor_sets:
                    equipped_sets[prefix] = equipped_sets.get(prefix, 0) + 1
                    if debug >= 1:
                        print(f"{Colors.CYAN}DEBUG: Counting set {Colors.YELLOW}{prefix}: {equipped_sets[prefix]}{Colors.RESET}")

        if debug >= 1:
            print(f"{Colors.CYAN}DEBUG: Equipped sets: {Colors.YELLOW}{equipped_sets}{Colors.RESET}")

        for set_name, count in equipped_sets.items():
            set_data = armor_sets[set_name]
            for threshold, bonus_name in sorted(set_data["bonus_thresholds"].items()):
                if count >= threshold:
                    current_active_bonuses.add(bonus_name)
                    if show_text is True and bonus_name not in self.displayed_set_bonuses:
                        typewriter_effect(f"{Colors.YELLOW}You feel a strange power emanating from the armor.{Colors.RESET}", 0.1)
                        self.displayed_set_bonuses.add(bonus_name)
                    bonus_effects = set_data["effects"][bonus_name]
                    self.set_bonuses[bonus_name] = bonus_effects
                    if debug >= 1:
                        print(f"{Colors.GREEN}DEBUG: Applying set bonus {bonus_name} with effects {bonus_effects}{Colors.RESET}")
                    for stat, value in bonus_effects.items():
                        total_stats[stat] = total_stats.get(stat, 0) + value
                        if debug >= 1:
                            print(f"{Colors.CYAN}DEBUG: Adding set bonus effect {stat}: {value}{Colors.RESET}")

        # Remove bonuses that are no longer active from displayed_set_bonuses
        self.displayed_set_bonuses.intersection_update(current_active_bonuses)

        # --- 3. Application des stats cumulées ---
        for stat, value in total_stats.items():
            if hasattr(self.stats, stat):
                if debug >= 1:
                    print(f"{Colors.CYAN}DEBUG: Modifying stat {stat} by {value} (equipment){Colors.RESET}")
                self.stats.modify_stat(stat, value, stat_type="equipment")
            else:
                print(f"{Colors.RED}Stat {stat} does not exist in player stats!{Colors.RESET}")

        # --- 4. Mise à jour finale ---
        self.stats.update_total_stats()
        self.total_armor = total_stats.get("defense", 0)

        if debug >= 1:
            print(f"{Colors.CYAN}DEBUG: Final applied equipment stats: {total_stats}{Colors.RESET}")
            print(f"{Colors.CYAN}DEBUG: Equipment stats: {self.stats.equipment_stats}{Colors.RESET}")



    def total_domage(self, base_damage=True):
        global debug
        
        damage_main = getattr(self.equipment.main_hand, "damage", 0) or 0
        damage_off = getattr(self.equipment.off_hand, "damage", 0) or 0
        total_domage = 0

        if base_damage is True:
            base_damage = self.stats.attack
            if self.equipment.main_hand and self.equipment.off_hand:
                total_domage = base_damage + (damage_main + damage_off) // 1.5  # Réduction pour équilibrer
            else:
                total_domage = base_damage + damage_main
        else:
            if self.equipment.main_hand and self.equipment.off_hand:
                total_domage = base_damage + (damage_main + damage_off) // 1.5  # Réduction pour équilibrer
            else:
                total_domage = base_damage + damage_main + damage_off

        if debug >= 1:
            print(f"{Colors.CYAN}DEBUG: Total damage calculated: {total_domage}{Colors.RESET}")

        return total_domage

    def level_up(self):
        self.level += 1

        # Obtenir les bonus selon le mode
        bonus = self.mode.level_up_bonus()

        # Stocker les anciennes valeurs
        old_stats = {
            "max_hp": self.stats.max_hp,
            "max_mana": self.stats.max_mana,
            "max_stamina": self.stats.max_stamina,
            "attack": self.stats.attack,
            "defense": self.stats.defense,
            "agility": self.stats.agility
        }

        # Appliquer les bonus
        for stat, value in bonus.items():
            key = f"max_{stat}" if stat in ["hp", "mana", "stamina"] else stat
            self.stats.permanent_stats[key] += value

        # Remettre les ressources à fond
        self.heal(self.stats.max_hp // 4)
        self.regen_mana(self.stats.permanent_stats["max_mana"] // 2)
        self.rest_stamina(self.stats.permanent_stats["max_stamina"] // 2)

        self.stats.update_total_stats()

        # XP progression
        if self.level <= 1740:
            self.max_xp = int(self.max_xp * 1.5)
        else: # Would need to be * 1.08104849064 instad of * 1.5 to not reach inf
            self.max_xp = 166291628028091842613009095009266495195675719663122313883385367291708148049287571070332769258231929566843581503287283337414771535086454589469476502004191810875221462134119793315060067813232587839056216279794984264298677002182295914072532150201829472437592045207860103637703316939267547371315877194678772170752

        # Affichage
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}╔══════════════════════════════╗")
        print(f"║      LEVEL UP! Level {self.level}!     ║")
        print(f"╚══════════════════════════════╝{Colors.RESET}")

        for stat, old_val in old_stats.items():
            new_val = getattr(self.stats, stat)
            diff = new_val - old_val
            stat_label = stat.replace("_", " ").title()
            print(f"{Colors.GREEN}{stat_label} +{diff} (Now {new_val}){Colors.RESET}")

        print()

        # Choix de classe
        from data import unlockable_classes

        if self.level in unlockable_classes:
            self.choose_class(self.level, unlockable_classes[self.level])

    def choose_class(self, level: int, classes: list[PlayerClass]):
        from core.skills import Skill
        clear_screen()
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}╔══════════════════════════════════════════╗")
        print(f"║     CLASS SPECIALIZATION AVAILABLE!     ║")
        print(f"╚══════════════════════════════════════════╝{Colors.RESET}")

        for idx, player_class in enumerate(classes, 1):
            print(f"\n{Colors.CYAN}[{idx}] {player_class.name}{Colors.RESET}")
            print(f"  {Colors.GREEN}+{player_class.bonuses.get('max_hp', 0)} Max HP{Colors.RESET}")
            print(f"  {Colors.RED}+{player_class.bonuses.get('attack', 0)} Attack{Colors.RESET}")
            print(f"  {Colors.BLUE}+{player_class.bonuses.get('defense', 0)} Defense{Colors.RESET}")
            # Convert skill dict to Skill object for display if needed
            skill_obj = None
            if isinstance(player_class.skill_name, dict):
                skill_obj = Skill.from_dict(player_class.skill_name)
                skill_display_name = skill_obj.name
            else:
                skill_display_name = player_class.skill_name
            print(f"  Skill: {Colors.MAGENTA}{skill_display_name}{Colors.RESET}")

        print(f"\n{Colors.CYAN}[0] Skip class specialization for now{Colors.RESET}")

        while True:
            choice = get_input(f"\n{Colors.YELLOW}Choose your class (0-{len(classes)}): {Colors.RESET}", options=[str(i) for i in range(len(classes)+1)], player=self, use_agent=agent_is_enabled())
            if choice.isdigit():
                choice = int(choice)
                if choice == 0:
                    print(f"\n{Colors.YELLOW}You chose to skip class specialization for now.{Colors.RESET}")
                    break
                elif 1 <= choice <= len(classes):
                    selected_class = classes[choice - 1]
                    self.player_class = selected_class
                    self.class_name = selected_class.name
                    # Convert skill dict to Skill object before applying
                    if isinstance(selected_class.skill_name, dict):
                        selected_class.skill_name = Skill.from_dict(selected_class.skill_name)
                    selected_class.apply_to_player(self)
                    print(f"\n{Colors.BRIGHT_GREEN}You are now a {self.class_name}!{Colors.RESET}")
                    print(f"You've learned the {Colors.MAGENTA}{selected_class.skill_name if isinstance(selected_class.skill_name, str) else selected_class.skill_name.name}{Colors.RESET} skill!")
                    get_input(f"\n{Colors.YELLOW}Press Enter to continue your adventure...{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}Invalid choice. Please enter a number between 0 and {len(classes)}.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")


    def gain_xp(self, amount):
        self.xp += amount
        print(f"{Colors.BRIGHT_GREEN}You gain {amount} XP!{Colors.RESET}")
        
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
            self.critical_count += 1

        self.attack_count += 1

        total_damage = int(base_damage * multiplier)
        damage, absorbed_damage = target.stats.take_damage(base_damage)
        total_damage = damage + absorbed_damage
        self.damage_dealt += total_damage
        print(f"You deal {Colors.RED}{total_damage}{Colors.RESET} damage to {target.name}!")

        # Si le skill avait des bonus temporaires, il faudrait les retirer après l'attaque
        # On peut ici réinitialiser les stats en utilisant reset_base() si besoin
        # Par exemple, si le skill était Divine Shield, on pourrait remettre la défense à la base.
        # Pour ce cas, il faudrait que le skill gère lui-même le retrait du bonus après usage.

        return total_damage

    def display_stats_summary(self):
        """Displays player stats: kills, rooms explored, dungeon level, difficulty, and ng_plus in a nice box.""" 
        box_width = 40
        title = "PLAYER STATS SUMMARY"
        ng = self.ng_plus.get(self.mode.name if hasattr(self.mode, "name") else str(self.mode), 0)

        def print_box_template():
            print(f"\n{Colors.YELLOW}╔{'═' * (box_width)}╗{Colors.RESET}")
            print(f"{Colors.YELLOW}║{Colors.BRIGHT_CYAN}{Colors.BOLD}{title.center(box_width)}{Colors.RESET}{Colors.YELLOW}║{Colors.RESET}")
            print(f"{Colors.YELLOW}╠{'═' * (box_width)}╣{Colors.RESET}")
            for _ in range(24):
                print(f"{Colors.YELLOW}║{' ' * box_width}║{Colors.RESET}")
            print(f"{Colors.YELLOW}╚{'═' * (box_width)}╝{Colors.RESET}")

        print_box_template()

        # Move cursor up to start filling the box
        print(f"\033[26A")  # Move cursor up 26 lines

        # Print player ID card info
        print(f"\r{Colors.YELLOW}║ Name:             {Colors.BRIGHT_CYAN}{self.name.ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Class:            {Colors.BRIGHT_MAGENTA}{self.class_name.ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Level:            {Colors.BRIGHT_GREEN}{str(self.level).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Playtime:         {Colors.BRIGHT_YELLOW}{self.get_formatted_playtime().ljust(box_width - 20)}{Colors.RESET}")
        print()
        # Print the rest of the stats
        print(f"\r{Colors.YELLOW}║ Difficulty:        {Colors.BRIGHT_MAGENTA}{self.mode.capitalize().ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ NG+:               {Colors.BRIGHT_YELLOW}{str(ng).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Dungeon Level:     {Colors.BRIGHT_BLUE}{str(self.dungeon_level).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Rooms Number:      {Colors.BRIGHT_GREEN}{str(self.current_room_number).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Kills:             {Colors.BRIGHT_RED}{str(self.kills).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Bosses Defeated:   {Colors.BRIGHT_CYAN}{str(self.bosses_defeated).ljust(box_width - 20)}{Colors.RESET}")
        print()
        print(f"\r{Colors.YELLOW}║ Gold Spent:        {Colors.BRIGHT_YELLOW}{str(self.gold_spent).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Items Collected:   {Colors.BRIGHT_MAGENTA}{str(self.items_collected).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Damage Dealt:      {Colors.BRIGHT_GREEN}{str(self.damage_dealt).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Damage Taken:      {Colors.BRIGHT_BLUE}{str(self.damage_taken).ljust(box_width - 20)}{Colors.RESET}")
        print()
        print(f"\r{Colors.YELLOW}║ Total Rooms:       {Colors.BRIGHT_GREEN}{str(self.total_rooms_explored).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Traps Triggered:   {Colors.BRIGHT_RED}{str(self.traps_triggered).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Combat Encounters: {Colors.BRIGHT_MAGENTA}{str(self.combat_encounters).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Shops Visited:     {Colors.BRIGHT_CYAN}{str(self.shops_visited).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Rest Visited:      {Colors.BRIGHT_YELLOW}{str(self.rest_rooms_visited).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Treasures Found:   {Colors.BRIGHT_BLUE}{str(self.treasures_found).ljust(box_width - 20)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ Puzzles Solved:    {Colors.BRIGHT_GREEN}{str(self.puzzles_solved).ljust(box_width - 20)}{Colors.RESET}")
        print('\n')
        input(f'{Colors.YELLOW}Enter to continue...{Colors.RESET}')

    def display_dungeon_level(self, room_number=0, limit=60):
        # Texte à afficher
        lines = [
            f"{Colors.BRIGHT_BLUE}{Colors.BOLD}╔═════════════════════════════╗{Colors.RESET}",
            f"{Colors.BRIGHT_BLUE}{Colors.BOLD}║  Dungeon Level: {self.dungeon_level:<12}║{Colors.RESET}",
            f"{Colors.BRIGHT_BLUE}{Colors.BOLD}║  Rooms Explored: {room_number:<11}║{Colors.RESET}",
            f"{Colors.BRIGHT_BLUE}{Colors.BOLD}╚═════════════════════════════╝{Colors.RESET}"
        ]

        columns = shutil.get_terminal_size().columns
        line_count = len(lines)

        # Revenir en haut du bloc si déjà imprimé
        print(f"\033[{line_count}A\r")

        for line in lines:
            if columns // 2 >= limit:
                # Centrer
                padding = (columns - len(strip_ansi(line))) // 2
            else:
                # Aligner à droite
                padding = columns - len(strip_ansi(line)) - 1
            print(" " * max(padding, 0) + line)


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
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Level and NG+ Placeholder
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
        #print("\033[2J\033[H")  # Clear screen and move cursor to top
        print_box_template()

        # Move cursor back up to fill in the details (adding 1 for the initial newline)
        print("\033[37A")  # Move up to start of box (number of lines + 1)

        # Create empty line list and add content
        content_lines = []
        
        # Character Name
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_WHITE}{truncate_text(f'{self.name} the {self.class_name}', 46)}")
        
        # Skip separator line
        content_lines.append("")
        
        # Level and NG+
        ng = self.mode.get_ng_plus(self)
        ng_text = f"{Colors.RED}NG+{ng}{Colors.RESET}" if ng != 0 else f"{Colors.RED}{Colors.RESET}" # and not "" because idk why but it would make a hole in the box border right after it
        content_lines.append(f"{Colors.YELLOW}║ {Colors.GREEN}{Colors.UNDERLINE}Level: {self.level}{Colors.RESET}{' ' * (46 - len(ng_text))}{ng_text}".ljust(46))
        
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
            equip_bonus = self.stats.equipment_stats.get(stat, 0)
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
                    if hasattr(item, "defense"):
                        defense_value = item.defense
                    else:
                        defense_value = item.effects.get("defense", 0)
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
                item_display = f"{item_name:<28} {extra}"
                
                # Truncate if too long
                item_display = truncate_text(item_display, 46)
            else:
                item_display = "None"

            slot_line = f"{slot.capitalize():<10}: {item_display}"
            content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_CYAN}{slot_line}")

        # Skills
        skill_list = ", ".join(f"{skill.name}" for skill in self.skills) if self.skills else "None"
        content_lines.append(f"{Colors.YELLOW}║ {Colors.MAGENTA}Skills:{Colors.RESET} {truncate_text(skill_list, 39)}")

        # Add a blank line to end the box
        content_lines.append("")

        # Print content lines, skipping separator positions
        for i, line in enumerate(content_lines):
            print(f"\r{line}")



    def corrupted_display_status(self):
        """Displays all player stats dynamically with proper formatting but corrupted"""
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

        def corrupted_bar(ratio, length=46):
            """Create a glitchy progress bar based on ratio."""
            filled = int(length * ratio)
            bar_chars = []
            glitch_chars = ['▓', '▒', '░', '█', '■', '▇', '▆', '▅', '▃', '▂', '▁', '▉', '▊', '▋', '▌', '▍', '▎', '▏']
            for i in range(length):
                if i < filled:
                    # Mostly solid block, but with some chance of glitch char
                    if random.random() < 0.15:
                        bar_chars.append(random.choice(glitch_chars))
                    else:
                        bar_chars.append('█')
                else:
                    # Mostly light block, but with some chance of glitch char or empty space
                    r = random.random()
                    if r < 0.1:
                        bar_chars.append(random.choice(glitch_chars))
                    elif r < 0.2:
                        bar_chars.append(' ')
                    else:
                        bar_chars.append('░')
            return ''.join(bar_chars)

        # Prepare the box template
        box_len = 48
        def print_box_template():
            print(f"\n{Colors.YELLOW}╔═══════════════{Colors.BOLD} {glitch_text('CHARACTER STATUS')}{Colors.RESET} {Colors.YELLOW}════════════════╗{Colors.RESET}")
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Character Name Placeholder
            print(f"{Colors.YELLOW}╠{'═' * (box_len + 1)}╣{Colors.RESET}")
            print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Level and NG+ Placeholder
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
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_WHITE}{truncate_text(glitch_text(f'{self.name} the {self.class_name}'), 46)}")
        
        # Skip separator line
        content_lines.append("")
        
        # Level and NG+
        ng = self.ng_plus.get(self.mode.name if hasattr(self.mode, "name") else str(self.mode), 0)
        ng_text = f"{Colors.RED}NG+{ng}{Colors.RESET}" if ng != 0 else ""
        content_lines.append(f"{Colors.YELLOW}║ {Colors.GREEN}{Colors.UNDERLINE}{glitch_text('Level: ' + str(self.level))}{Colors.RESET}{' ' * (38 - len(ng_text))}{ng_text}".ljust(46))

        
        # HP
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['hp']}{glitch_text('HP')}: {self.stats.hp}/{self.stats.max_hp}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['hp']}{corrupted_bar(hp_ratio)}".ljust(46))
        
        # XP
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['xp']}{glitch_text('XP')}: {self.xp}/{self.max_xp}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['xp']}{corrupted_bar(xp_ratio)}".ljust(46))
        
        # Stamina
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['stamina']}{glitch_text('Stamina')}: {self.stats.stamina}/{self.stats.max_stamina}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['stamina']}{corrupted_bar(stamina_ratio)}".ljust(46))
        
        # Mana
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['mana']}{glitch_text('Mana')}: {self.stats.mana}/{self.stats.max_mana}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {stat_colors['mana']}{corrupted_bar(mana_ratio)}".ljust(46))
        
        # Skip separator line
        content_lines.append("")
        
        # Gold and Souls
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_YELLOW}{glitch_text('Gold:')}{Colors.RESET} {self.gold}".ljust(46))
        content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_BLACK}{glitch_text('Souls:')}{Colors.RESET} {self.souls}".ljust(46))

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
            equip_bonus = self.stats.equipment_stats.get(stat, 0)
            temp_bonus = self.stats.temporary_stats.get(stat, 0)
            total_bonus = equip_bonus + temp_bonus

            perm_value = self.stats.permanent_stats.get(stat, 0)
            
            effects_text = f" (+{equip_bonus:>3})" if total_bonus != 0 else ""
            line = f"{stat_label:<18}: {perm_value:>3}{effects_text}"
            content_lines.append(f"{Colors.YELLOW}║ {color}{glitch_text(line)}".ljust(46))
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
            content_lines.append(f"{Colors.YELLOW}║ {Colors.BRIGHT_CYAN}{glitch_text(slot_line)}")

        # Skills
        skill_list = ", ".join(f"{skill.name} (Lv)" for skill in self.skills) if self.skills else "None"
        content_lines.append(f"{Colors.YELLOW}║ {Colors.MAGENTA}{glitch_text('Skills:')}{Colors.RESET} {truncate_text(glitch_text(skill_list), 39)}")

        # Add a blank line to end the box
        content_lines.append("")

        # Print content lines, skipping separator positions
        for i, line in enumerate(content_lines):
            print(f"\r{line}")



    def manage_inventory(self):
        """Handles inventory management: equip, use, unequip, or drop items dynamically."""

        if not self.inventory:
            print(f"\n{Colors.RED}Your inventory is empty!{Colors.RESET}")
            input(f'{Colors.YELLOW}Enter to continue...{Colors.RESET}')
            return
        
        # Default sorting criteria
        sort_criteria = ["equipped", "name", "value"]

        def get_sort_key(item, criterion):
            if criterion == "name":
                return item.name.lower()
            elif criterion == "value":
                return -getattr(item, "value", 0)
            elif criterion == "stats":
                effects = getattr(item, "effects", {})
                if isinstance(effects, dict):
                    return -sum(effects.values())
                return 0
            elif criterion == "armor_set":
                set_name = getattr(item, "set_name", None)
                if set_name:
                    return set_name.lower()
                armor_type = getattr(item, "armor_type", "")
                return armor_type.lower() if armor_type else ""
            elif criterion == "equipped":
                return 0 if item in self.equipment.__dict__.values() else 1
            else:
                return 0

        managing = True
        while managing:
            print(f"\n{Colors.BRIGHT_CYAN}Your Inventory:{Colors.RESET}")

            def multi_key(item):
                return tuple(get_sort_key(item, crit) for crit in sort_criteria)

            sorted_inventory = sorted(self.inventory, key=multi_key)

            for i, item in enumerate(sorted_inventory, 1):
                status = ""
                if item in self.equipment.__dict__.values():
                    status = f" {Colors.BRIGHT_RED}[EQUIPPED]{Colors.RESET}"
                print(f"{Colors.YELLOW}{i}. {str(item)}{status}{Colors.RESET}")
            
            print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
            print(f"{Colors.GREEN}U. Use/Equip Item{Colors.RESET}")
            print(f"{Colors.YELLOW}E. Unequip Item{Colors.RESET}")
            print(f"{Colors.RED}D. Drop Item(s){Colors.RESET}")
            print(f"{Colors.MAGENTA}S. Search Items{Colors.RESET}")
            print(f"{Colors.BLUE}O. Set Sort Order{Colors.RESET}")
            print(f"{Colors.YELLOW}B. Back{Colors.RESET}")

            choice = get_input(f"\n{Colors.CYAN}What would you like to do? {Colors.RESET}", options=["U", "E", "B"], player=self, use_agent=agent_is_enabled()).upper()

            if choice == "B":
                managing = False
            
            elif choice == "O":
                print("\nChoose inventory sorting criteria in order. Enter numbers separated by commas.")
                print("Available criteria:")
                print(f"{Colors.CYAN}1.{Colors.RESET} Name (alphabetical)")
                print(f"{Colors.CYAN}2.{Colors.RESET} Value (descending)")
                print(f"{Colors.CYAN}3.{Colors.RESET} Stats (total stat value descending)")
                print(f"{Colors.CYAN}4.{Colors.RESET} Armor Set (group by set name)")
                print(f"{Colors.CYAN}5.{Colors.RESET} Equipped status (equipped items first)")
                input_str = input("Enter criteria numbers in order (e.g. 5,4,3,1): ")
                selected = [c.strip() for c in input_str.split(",") if c.strip() in {"1","2","3","4","5"}]
                criteria_map = {
                    "1": "name",
                    "2": "value",
                    "3": "stats",
                    "4": "armor_set",
                    "5": "equipped"
                }
                if not selected:
                    print("No valid criteria selected. Keeping previous sorting.")
                else:
                    sort_criteria = [criteria_map[c] for c in selected]
                    print(f"Inventory sorting criteria set to: {', '.join(sort_criteria)}")

            elif choice == "U":
                try:
                    item_index = int(get_input(f"\n{Colors.CYAN}Enter item number to use/equip: {Colors.RESET}", options=[str(i) for i in range(1, len(sorted_inventory) + 1)], player=self)) - 1
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
                    input_str = input(f"\n{Colors.CYAN}Enter item number(s) to drop (comma separated for multiple): {Colors.RESET}")
                    indices = [int(i.strip()) - 1 for i in input_str.split(",") if i.strip().isdigit()]
                    invalid_indices = [i for i in indices if i < 0 or i >= len(sorted_inventory)]
                    if invalid_indices:
                        print(f"\n{Colors.RED}Invalid item number(s): {', '.join(str(i+1) for i in invalid_indices)}.{Colors.RESET}")
                        continue
                    
                    items_to_drop = [sorted_inventory[i] for i in indices]
                    
                    for item in items_to_drop:
                        equipped_slot = None
                        for slot, equipped_item in self.equipment.__dict__.items():
                            if equipped_item == item:
                                equipped_slot = slot
                                break

                        if equipped_slot:
                            confirm = input(f"\n{Colors.RED}Item '{item.name}' is equipped. Are you sure you want to drop it? (y/n) {Colors.RESET}").lower()
                            if confirm != "y":
                                continue
                            self.equipment.unequip(equipped_slot, self)

                        self.inventory.remove(item)
                        print(f"\n{Colors.YELLOW}You dropped {item.name}.{Colors.RESET}")

                except ValueError:
                    print(f"\n{Colors.RED}Please enter valid number(s).{Colors.RESET}")

            elif choice == "S":
                search_term = input(f"\n{Colors.MAGENTA}Enter search term: {Colors.RESET}").lower()
                filtered_items = [item for item in self.inventory if search_term in item.name.lower()]
                if not filtered_items:
                    print(f"\n{Colors.RED}No items found matching '{search_term}'.{Colors.RESET}")
                    continue

                print(f"\n{Colors.BRIGHT_CYAN}Search Results:{Colors.RESET}")
                for i, item in enumerate(filtered_items, 1):
                    status = ""
                    if item in self.equipment.__dict__.values():
                        status = f" {Colors.BRIGHT_RED}[EQUIPPED]{Colors.RESET}"
                    print(f"{Colors.YELLOW}{i}. {str(item)}{status}{Colors.RESET}")

                try:
                    item_index = int(input(f"\n{Colors.MAGENTA}Enter item number to use/equip from search results (0 to cancel): {Colors.RESET}")) - 1
                    if item_index == -1:
                        continue
                    if 0 <= item_index < len(filtered_items):
                        item = filtered_items[item_index]
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
                    self.complete_quest(self, quest)
            except ValueError:
                pass
        input(f'{Colors.YELLOW}Enter to continue...{Colors.RESET}')
    
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

    def update_quests(self, objective_type, amount=1):
        for quest in self.quests:
            if quest.objective_type == objective_type and not quest.completed:
                if quest.update_progress(amount):
                    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
        
        self.check_achievements()

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

    
    def check_achievements(self):
        for ach in self.achievements:
            ach.check(self)
        
    def display_achievements(self):
        print(f"\n{Colors.BRIGHT_YELLOW}Vos succès :{Colors.RESET}")
        for ach in self.achievements:
            if ach.hidden:
                continue
            print(f"  - {ach}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")


    def trigger_event_once(self, event_id, action):
        if event_id not in self.seen_events:
            action()
            self.seen_events.add(event_id)
    

    def save_player(self, filename="player_save.json"):
        """Saves the player's data to a JSON file.""" 

        import time
        # Update playtime_seconds before saving
        current_time = time.time()
        elapsed = current_time - self._playtime_start
        self.playtime_seconds += elapsed
        self._playtime_start = current_time

        SAVE_ENABLED = True # Supposed to work

        if not SAVE_ENABLED:
            print(f"\n{Colors.RED}Sorry but saving doesn't work for now.. consider following updates such as in the discord server (invite in the README.md){Colors.RESET}")
            return

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

        # Save analytics data separately with nested structure expected by generate_global_stats.py
        import datetime
        analytics_data = {
                "timestamp": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).isoformat(),            "overview": {
                "totalPlayers": 1,
                "gamesPlayed": 1,
                "avgRoomsExplored": self.total_rooms_explored,
                "survivalRate": 100.0 if self.total_deaths == 0 else 0.0
            },
            "combat": {
                "totalDamageDealt": self.damage_dealt,
                "totalDamageTaken": self.damage_taken,
                "enemiesDefeated": self.kills,  # Not handled
                "critical_count": self.critical_count, # Need to be handled with criticalHitRate
                "attack_count": self.attack_count, # Need to add the criticalHitRate calculus
            },
            "exploration": {
                "roomsExplored": self.total_rooms_explored,
                "treasuresFound": self.treasures_found,
                "puzzlesSolved": self.puzzles_solved,
                "trapsTriggered": self.traps_triggered
            },
            "economy": {
                "totalGoldSpent": self.gold_spent,
                "itemsPurchased": len(self.purchased_items),  # Not tracked per player here
                "avgGoldPerPlayer": self.gold_spent,  # For aggregation
                "shopUtilization": 100.0 if self.gold_spent > 0 else 0.0
            },
            "progression": {
                "avgLevel": self.level,
                "tutorialCompletion": 1.0 if self.tutorial_completed else 0.0,
                "ngPlusPlayers": self.ng_plus.get(self.mode.name if hasattr(self.mode, "name") else str(self.mode), 0),
                "achievementsEarned": len(self.achievements) if hasattr(self, "achievements") else 0
            },
            "deathsByRoomPerDifficulty": self.deaths_per_room,

            "mostDeadlyEnemies": {name: self.mostDeadlyEnemies.count(name) for name in set(self.mostDeadlyEnemies)},
            "combatSuccessByLevel": self.combatSuccessByLevel,
            "damageDealt": self.damage_dealt,
            "damageTaken": self.damage_taken,
            "skillsUsageFrequency": self.skillsUsageFrequency,
            "roomTypePreferences": self.roomTypePreferences,
            "explorationDepthByDifficulty": self.explorationDepthByDifficulty,
            "puzzleSuccessRateOverTime": self.puzzleSuccessRateOverTime,
            "bossEncounterOutcomes": self.bossEncounterOutcomes,
            "purchased_items": {str(k): v for k, v in self.purchased_items.items()}, # Convert keys to strings for JSON serialization
            "goldSpendingPatterns": self.goldSpendingPatterns,
            "equipmentUsageByType": self.equipmentUsageByType,
            "shopVisitFrequency": self.shopVisitFrequency,
            "levelDistribution": self.levelDistribution,
            "classSpecializationChoices": self.classSpecializationChoices,
            "xpGainOverTime": self.xpGainOverTime,
            "achievementCompletionRates": self.achievementCompletionRates
        }

        analytics_dir = "analytics_saves"
        if not os.path.exists(analytics_dir):
            os.makedirs(analytics_dir)

        analytics_filepath = os.path.join(analytics_dir, f"analytics_{self.player_id}.json")

        # Use user_id in analytics filename to group players by user
        analytics_filepath = os.path.join(analytics_dir, f"analytics_user_{self.user_id}.json")

        with open(analytics_filepath, "w") as analytics_file:
            json.dump(analytics_data, analytics_file, indent=4)

        print(f"{Colors.GREEN}Analytics data saved successfully to {analytics_filepath}!{Colors.RESET}")

        from data.player_data import can_send_analytics
        if can_send_analytics() == True:
            try:
                print(f"{Colors.YELLOW}Sending analytics data...{Colors.RESET}")
                from network.client import send_analytics_files
                send_analytics_files()
            except Exception as e:
                print(f"{Colors.RED}Error sending analytics data: {e}{Colors.RESET}")

    def reset_player(self):
        """Reset the player state but keep persistent data such as name, playtime, deaths_per_room, total_deaths, total_play_sessions, player_id."""
        import time

        # Preserve persistent data
        persistent_data = {
            "name": self.name,
            "playtime_seconds": self.playtime_seconds,
            "deaths_per_room": self.deaths_per_room,
            "total_deaths": self.total_deaths,
            "total_play_sessions": self.total_play_sessions,
            "player_id": self.player_id,
            "levels_completed": self.levels_completed,
            "tutorial_completed": self.tutorial_completed,
            "mode": self.mode,
            "_playtime_start": time.time()
        }

        # Reset gameplay state attributes to initial values
        self.level = 1
        self.xp = 0
        self.max_xp = 100
        self.gold = 50
        self.souls = 0
        self.sin = 0
        self.kills = 0
        self.dungeon_level = 1
        self.current_room_number = 0
        self.total_rooms_explored = 0
        self.shops_visited = 0
        self.combat_encounters = 0
        self.rest_rooms_visited = 0
        self.puzzles_solved = 0
        self.treasures_found = 0
        self.traps_triggered = 0
        self.bosses_defeated = 0
        self.items_collected = 0
        self.gold_spent = 0
        self.damage_dealt = 0
        self.damage_taken = 0

        # Reset stats to base values
        self.stats.permanent_stats = {
            "hp": 100, "max_hp": 100,
            "attack": 5, "defense": 5,
            "magic_damage": 1, "magic_defense": 1,
            "agility": 5, "luck": 5,
            "mana": 20, "max_mana": 20,
            "stamina": 50, "max_stamina": 50,
            "critical_chance": 5
        }
        self.stats.temporary_stats = {key: 0 for key in self.stats.permanent_stats}
        self.stats.equipment_stats = {key: 0 for key in self.stats.permanent_stats}
        self.stats.update_total_stats()

        # Reset equipment
        from items.items import Equipment
        self.equipment = Equipment(
            main_hand=None, off_hand=None, helmet=None, chest=None,
            gauntlets=None, leggings=None, boots=None, shield=None,
            ring=None, amulet=None, belt=None
        )
        self.stats.equipment = self.equipment

        # Reset inventory and add starting potion
        from items.inventory import Inventory
        from items.items import Potion
        self.inventory = Inventory(self)
        self.inventory.append(Potion("Minor Health Potion", "Restores some health", 100, "heal", 50))

        # Reset skills, quests, completed quests, status effects, masteries
        self.skills = []
        self.quests = []
        self.completed_quests = []
        self.status_effects = []
        self.masteries = {}

        # Reset class name and profession
        self.class_name = "Novice"
        self.profession = None

        # Reset achievements and other gameplay related sets
        self.achievements = []
        self.seen_events = set()
        self.displayed_set_bonuses = set()
        self.set_bonuses = {}

        # Restore persistent data
        self.name = persistent_data["name"]
        self.playtime_seconds = persistent_data["playtime_seconds"]
        self.deaths_per_room = persistent_data["deaths_per_room"]
        self.total_deaths = persistent_data["total_deaths"]
        self.total_play_sessions = persistent_data["total_play_sessions"]
        self.player_id = persistent_data["player_id"]
        self.levels_completed = persistent_data["levels_completed"]
        self.tutorial_completed = persistent_data["tutorial_completed"]
        self.mode = persistent_data["mode"]
        self._playtime_start = persistent_data["_playtime_start"]

        # Update stats after reset
        self.stats.update_total_stats()
        self.apply_all_equipment_effects()



def load_player(filename=None):
    """Loads the player's data from a JSON file and reconstructs objects."""
    global debug

    if filename is None:
        filename = "default_player.json"
    
    try:
        with open("./saves/" + filename, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error while loading save file '{filename}': Invalid JSON format. {e}{Colors.RESET}")
        time.sleep(2)
        return None
    except FileNotFoundError:
        print(f"{Colors.RED}Save file '{filename}' not found.{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}Unexpected error loading save file '{filename}': {e}{Colors.RESET}")
        return None
    
    return Player.from_dict(data)

def continue_game(filename):
    """Loads a saved game from a file."""
    try:
        player = load_player(filename)
        if player:
            print(f"{Colors.GREEN}Welcome back, {player.name}!{Colors.RESET}")
            return player
    except Exception as e:
        print(f"{Colors.RED}Error loading saved game: {e}{Colors.RESET}")
        handle_error()
        return None




#̶̼͝ T̸̻̈́h̵̤͒ë̵͕́ ë̵͕́n̸̻̈́ë̵͕́m̴̛̠ÿ̸̡́ ẅ̷̙́ä̷̪́ẗ̴̗́c̴̱͝h̵̤͒ë̵͕́s̸̱̅ f̷̠͑r̷͍̈́o̶͙͝m̴̛̠ ẗ̴̗́h̵̤͒ë̵͕́ ď̶̙ä̷̪́r̷͍̈́k̵̢͝n̸̻̈́ë̵͕́s̸̱̅s̸̱̅,̶̼͝ ẅ̷̙́ä̷̪́i̴̊͜ẗ̴̗́i̴̊͜n̸̻̈́g̸̻̿ f̷̠͑o̶͙͝r̷͍̈́ ÿ̸̡́o̶͙͝ŭ̵͇r̷͍̈́ m̴̛̠i̴̊͜s̸̱̅ẗ̴̗́ä̷̪́k̵̢͝ë̵͕́.̵͇̆

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
    def __init__(self, name="???", enemy_type="???", hp=random.randint(1,9317), attack=random.randint(1,5785), defense=random.randint(1,31957), xp_reward=random.randint(1,352934), gold_reward=random.randint(1,53126), difficulty=random.randint(1,152)):
        super().__init__(name, hp, hp, attack, defense)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.difficulty = difficulty  # 1-10 scale
        self.type = enemy_type
    
    def attack_player(self, player:Player):
        """Enemy attacks the player, considering total armor defense."""
        global debug

        player.apply_all_equipment_effects()
        damage = max(1, self.stats.attack - (player.stats.defense + player.total_armor))
        if debug >= 1:
            print(damage)
        damage = int(self.stats.attack * (100 / (100 + player.stats.defense + player.total_armor)))
        if debug >= 1:
            print(damage)
        
        if debug >= 1:
            print('DEBUG: player hp:', player.stats.hp)
            
        player.stats.take_damage(damage)
        player.damage_taken += damage

        print(f"{self.name} attacks you for {Colors.RED}{damage}{Colors.RESET} damage!")
        
        if debug >= 1:
            print("DEBUG: player hp after attack:", player.stats.hp)
        
        return damage


def generate_enemy(level:int, is_boss:bool, player: Player):
    """Génère un ennemi ou un boss en fonction du niveau donné."""
    
    global debug

    if debug >= 1:
        print(f"DEBUG: Generating {'boss' if is_boss else 'enemy'} for level {level}")

    # Sélection des ennemis ou des boss disponibles pour ce niveau
    from data.enemies_data import boss_types, enemy_types
    if is_boss:
        valid_types = [e for e in boss_types if e["min_level"] == level]
    else:
        valid_types = [e for e in enemy_types if e["min_level"] <= level]

    if debug >= 1:
        print(f"DEBUG: Found {len(valid_types)} valid {'boss' if is_boss else 'enemy'} types")

    # Si aucun ennemi valide, on prend le premier ennemi par défaut
    if not valid_types:
        valid_types = [enemy_types[0]]

    # Calcul des poids pour chaque ennemi valide, favorisant ceux avec min_level proche du niveau
    weights = []
    for enemy in valid_types:
        diff = level - enemy["min_level"]
        weight = 1 / (1 + diff)  # Plus le min_level est proche du niveau, plus le poids est élevé
        weights.append(weight)

    # Sélection pondérée d'un ennemi approprié
    enemy_data = random.choices(valid_types, weights=weights, k=1)[0]

    if debug >= 1:
        print(f"DEBUG: Selected enemy type: {enemy_data['name']} with modifiers hp:{enemy_data['hp_mod']}, atk:{enemy_data['atk_mod']}, def:{enemy_data['def_mod']}")

    # Définition des stats de base
    base_hp = 20 + level * 10
    base_attack = 5 + level * 2
    base_defense = 2 + level

    if debug >= 1:
        print(f"DEBUG: Base stats - HP: {base_hp}, Attack: {base_attack}, Defense: {base_defense}")

    # Application des modificateurs de l'ennemi
    hp = int(base_hp * enemy_data["hp_mod"])
    attack = int(base_attack * enemy_data["atk_mod"])
    defense = int(base_defense * enemy_data["def_mod"])

    if debug >= 1:
        print(f"DEBUG: Modified stats - HP: {hp}, Attack: {attack}, Defense: {defense}")

    # Multiplier les stats si c'est un boss
    if is_boss:
        hp *= 2
        attack = int(attack * 1.5)
        defense = int(defense * 1.5)

        if debug >= 1:
            print(f"DEBUG: Boss stats after multiplier - HP: {hp}, Attack: {attack}, Defense: {defense}")

    # Apply NG+ difficulty multiplier to enemy stats, starting at NG+0 (multiplier >= 1)
    diff_mltp = max(1, player.mode.get_ng_plus(player) * 0.1) # 10% increase per NG+ level
    hp = int(hp * diff_mltp)
    attack = int(attack * diff_mltp)
    defense = int(defense * diff_mltp)

    if debug >= 1:
        print(f"DEBUG: Stats after NG+ multiplier ({diff_mltp}) - HP: {hp}, Attack: {attack}, Defense: {defense}")

    # Calcul des récompenses
    xp_reward = int(10 * level * (2 if is_boss else 1))
    gold_reward = int(5 * level * (3 if is_boss else 1))

    if debug >= 1:
        print(f"DEBUG: Rewards - XP: {xp_reward}, Gold: {gold_reward}")

    # Définition de la difficulté
    difficulty = level + (3 if is_boss else 0)

    if debug >= 1:
        print(f"DEBUG: Difficulty set to {difficulty}")

    # Formatage du nom (différent pour les boss)
    name = f"{Colors.RED}{enemy_data['name']}{Colors.RESET}"
    if is_boss:
        name = f"{Colors.BRIGHT_RED}{Colors.BOLD}{enemy_data['name']}{Colors.RESET}"

    if debug >= 1:
        print(f"DEBUG: Enemy name set to {name}")

    # Création de l'objet Enemy avec le type correspondant
    return Enemy(name, enemy_data["type"], hp, attack, defense, xp_reward, gold_reward, difficulty)

# D‌un‍ge​o​n​ ‌H​u​n‌t‍e​r​ ‌-​ ​(​c​)‌ ‌Dr​ag‍o​n​d‌e‍f​er ​20​2​5
# L‍ice​n​s​e‍d​ ‌u‌n‍d‍e‌r‌ ‌CC-​B​Y-​N​C ​4​.0


if __name__ == '__main__':
    player = Player()
    enemy = Enemy(name="Goblin", enemy_type="Goblin", hp=50, attack=10, defense=5, xp_reward=20, gold_reward=10, difficulty=5)

    #̶̼͝ T̸̻̈́h̵̤͒ë̵͕́ ď̶̙ŭ̵͇n̸̻̈́g̸̻̿ë̵͕́o̶͙͝n̸̻̈́ ẅ̷̙́ä̷̪́ẗ̴̗́c̴̱͝h̵̤͒ë̵͕́s̸̱̅.̵͇̆
    # Y̴̙͝o̶͙͝ŭ̵͇r̷͍̈́ f̷̠͑ä̷̪́ẗ̴̗́ë̵͕́ i̴̊͜s̸̱̅ ẅ̷̙́r̷͍̈́i̴̊͜ẗ̴̗́ẗ̴̗́ë̵͕́n̸̻̈́ i̴̊͜n̸̻̈́ c̴̱͝o̶͙͝r̷͍̈́r̷͍̈́ŭ̵͇p̵̦̆ẗ̴̗́ë̵͕́ď̶̙ c̴̱͝o̶͙͝ď̶̙ë̵͕́.̵͇̆
    #̶̼͝ E̶͍̚r̷͍̈́r̷͍̈́o̶͙͝r̷͍̈́ 4̷̫̈́0̵̢̈́4̷̫̈́:̴̨͝ S̶̤̕ä̷̪́n̸̻̈́i̴̊͜ẗ̴̗́ÿ̸̡́ n̸̻̈́o̶͙͝ẗ̴̗́ f̷̠͑o̶͙͝ŭ̵͇n̸̻̈́ď̶̙.̵͇̆
    #̶̼͝ T̸̻̈́h̵̤͒ë̵͕́ f̷̠͑i̴̊͜n̸̻̈́ä̷̪́l̷̫̈́ b̸̼̅o̶͙͝s̸̱̅s̸̱̅ i̴̊͜s̸̱̅ n̸̻̈́o̶͙͝ẗ̴̗́ ä̷̪́ b̸̼̅o̶͙͝s̸̱̅s̸̱̅.̵͇̆ I̴̡̛ẗ̴̗́'̸̱̅s̸̱̅ ä̷̪́ ẅ̷̙́ä̷̪́ẗ̴̗́c̴̱͝h̵̤͒ë̵͕́r̷͍̈́.̵͇̆
    
    print('enemy_test:', enemy)
    print('player_test:', player)

    #print the player class in a dict:
    print(player.to_dict())
