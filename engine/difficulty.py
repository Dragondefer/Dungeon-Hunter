from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.entity import Player
    from engine.dungeon import Room

__version__ = "92.0"
__creation__ = "08-05-2025"

# D​u​ng​eo​n​ ​H​un​te​r​ ​-​ ​(​c​)​ ​Dr​ago​nd​e​f​e​r​ ​20​2​5
# L​i​c​en​s​ed​ ​un​d​e​r​ ​CC​-​B​Y-​N​C​ 4​.​0

import random

from data import EVENTS
from interface import Colors
from .game_utility import clear_screen, typewriter_effect
from .logger import logger
from .game_utility import sleep, loading, execute_command
import config


debug = 0

class GameMode:
    def __init__(self, name="normal"):
        self.name = name
    
    def __str__(self):
        return self.name # str(self.difficulty) return "normal"

    def capitalize(self):
        return self.name.capitalize()  # Now we can call `self.difficulty.capitalize()` and not get an AttributeError

    def to_dict(self):
        """Serialize the GameMode to a dictionary."""
        return {"name": self.name}

    @classmethod
    def from_dict(cls, data):
        """Deserialize a GameMode from a dictionary."""
        name = data.get("name", "normal")
        if name == "normal":
            return NormalMode()
        elif name == "soul_enjoyer":
            return SoulsEnjoyerMode()
        elif name == "realistic":
            return RealisticMode()
        elif name == "hardcore":
            return HardcoreMode()
        elif name == "puzzle":
            return PuzzleMode()
        else:
            # Default fallback
            return NormalMode()


    # ----- Combat -----

    def take_damage(self, player, damage):
        raise NotImplementedError

    def on_combat_start(self, player, enemy):
        """Hook called at the start of combat."""
        pass

    def modify_damage_dealt(self, player, damage):
        """Modify damage dealt by player."""
        return damage

    def modify_damage_taken(self, player, damage):
        """Modify damage taken by player."""
        return damage

    def _display_combat_status(self, player, enemy):
        clear_screen()
        # Display player status box similar to player.display_status with fixed box template and colored bars
        box_len = 48
        def create_bar(current, maximum, length=30, color=Colors.WHITE):
            ratio = current / maximum if maximum > 0 else 0
            filled = int(length * ratio)
            bar = color + "█" * filled + Colors.RESET + "░" * (length - filled)
            return bar

        # Print fixed box template with yellow outlines
        print(f"\n{Colors.YELLOW}╔═════════════════ {Colors.BOLD}COMBAT STATUS{Colors.RESET}{Colors.YELLOW} ═════════════════╗{Colors.RESET}")
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Player Name Placeholder
        print(f"{Colors.YELLOW}╠{'═' * (box_len + 1)}╣{Colors.RESET}")
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # HP Text Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # HP Bar Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Stamina Text Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Stamina Bar Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Mana Text Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Mana Bar Placeholder
        print(f"{Colors.YELLOW}╠{'═' * (box_len + 1)}╣{Colors.RESET}")
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Enemy Name Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Enemy HP Text Placeholder
        print(f"{Colors.YELLOW}║ {' ' * box_len}║{Colors.RESET}")  # Enemy HP Bar Placeholder
        print(f"{Colors.YELLOW}╚{'═' * (box_len + 1)}╝{Colors.RESET}")


        # Move cursor back up to fill in the details (number of lines + 1)
        print("\033[14A")

        # Player Name
        name_line = f"{player.name} the {player.class_name}"
        print(f"\r{Colors.YELLOW}║ {Colors.BRIGHT_WHITE}{name_line.ljust(box_len)}{Colors.RESET}")

        # Skip separator line
        print("\033[1B", end="")

        # HP
        hp_text = f"HP: {player.stats.hp}/{player.stats.max_hp}"
        hp_bar = create_bar(player.stats.hp, player.stats.max_hp, length=45, color=Colors.RED)
        print(f"\r{Colors.YELLOW}║ {Colors.RED}{hp_text.ljust(box_len)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ {hp_bar.ljust(box_len)}{Colors.RESET}")

        # Stamina
        stamina_text = f"Stamina: {player.stats.stamina}/{player.stats.max_stamina}"
        stamina_bar = create_bar(player.stats.stamina, player.stats.max_stamina, length=45, color=Colors.YELLOW)
        print(f"\r{Colors.YELLOW}║ {Colors.YELLOW}{stamina_text.ljust(box_len)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ {stamina_bar.ljust(box_len)}{Colors.RESET}")

        # Mana
        mana_text = f"Mana: {player.stats.mana}/{player.stats.max_mana}"
        mana_bar = create_bar(player.stats.mana, player.stats.max_mana, length=45, color=Colors.BRIGHT_BLUE)
        print(f"\r{Colors.YELLOW}║ {Colors.BRIGHT_BLUE}{mana_text.ljust(box_len)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ {mana_bar.ljust(box_len)}{Colors.RESET}")

        logger.info(f"Player: {player.stats.hp}/{player.stats.max_hp} hp, {player.stats.stamina}/{player.stats.max_stamina} stm, {player.stats.mana}/{player.stats.max_mana} mana")

        # Skip separator line
        print("\033[1B", end="")

        # Enemy Name
        enemy_name_line = f"Enemy: {enemy.name}"
        print(f"\r{Colors.YELLOW}║ {Colors.BRIGHT_WHITE}{enemy_name_line.ljust(box_len)}{Colors.RESET}")

        # Enemy HP
        enemy_hp_text = f"HP: {enemy.stats.hp}/{enemy.stats.max_hp}"
        enemy_hp_bar = create_bar(enemy.stats.hp, enemy.stats.max_hp, length=45, color=Colors.RED)
        print(f"\r{Colors.YELLOW}║ {Colors.RED}{enemy_hp_text.ljust(box_len)}{Colors.RESET}")
        print(f"\r{Colors.YELLOW}║ {enemy_hp_bar.ljust(box_len)}{Colors.RESET}")

        logger.info(f"{enemy.name}: {enemy.stats.hp}/{enemy.stats.max_hp} hp")

        # Bottom border
        print(f"{Colors.YELLOW}╚{'═' * (box_len + 1)}╝{Colors.RESET}")

    def _prepare_tutorial_enemy(self, player: Player, room: Room, is_boss_room, tutorial):
        global debug
        from core.entity import generate_enemy
        if tutorial is True and not room.enemies:
            if is_boss_room is False:
                if debug>=1: print("tutorial enemy generating")
                room.enemies.append(generate_enemy(player.dungeon_level, False, player))
                room.enemies[0].name = "Tutorial Goblin"
                room.enemies[0].stats.max_hp *= 2
                room.enemies[0].stats.hp *= 2
                room.enemies[0].stats.update_total_stats()
                if debug>=1: print("enemy generated:", room.enemies)

            elif is_boss_room is True:
                if debug>=1: print("tutorial boss generating")
                room.enemies.append(generate_enemy(player.dungeon_level, True, player))
                if debug>=1: print("boss generated:", room.enemies)


    def _show_tutorial_intro(self, is_boss_room):
        if not is_boss_room:
            typewriter_effect(
                f"\n[Assistant]: {Colors.GREEN}In this tutorial, you will learn the basics of combat{Colors.RESET}",
                0.03 * config.game_speed_multiplier,
            )
            sleep(0.5)
            typewriter_effect(
                f"[Assistant]: {Colors.GREEN}During combat, you have to manage your Health, Stamina and Mana.{Colors.RESET}",
                0.04 * config.game_speed_multiplier,
            )
            sleep(0.5)
        else:
            typewriter_effect(
                f"\n[Assistant]: {Colors.GREEN}This is your first combat against a boss.{Colors.RESET}",
                0.05 * config.game_speed_multiplier,
            )
            sleep(0.5)
            typewriter_effect(
                f"[Assistant]: {Colors.GREEN}Don't worry, I will help you if needed.{Colors.RESET}",
                0.05 * config.game_speed_multiplier,
            )
            sleep(0.5)
    
    def _show_action_tutorial(self, is_boss_room):
        if is_boss_room is False:
            typewriter_effect(f"\n[Assistant]: {Colors.GREEN}You can attack, use skills, or items during your turn.{Colors.RESET}", 0.03 * config.game_speed_multiplier)
            sleep(0.5)
            typewriter_effect(f"[Assistant]: {Colors.GREEN}You can also try to run away from the fight.{Colors.RESET}", 0.03 * config.game_speed_multiplier)
        else:
            typewriter_effect(f"\n[Assistant]: {Colors.GREEN}The boss is strong, be careful.{Colors.RESET}", 0.03 * config.game_speed_multiplier)
            sleep(0.5)
            """
            typewriter_effect(f"[Assistant]: {Colors.GREEN}You arn't alone..{Colors.RESET}", 0.03, "")
            sleep(0.5)
            typewriter_effect(f"{Colors.GREEN}for now.{Colors.RESET}", 0.03)
            sleep(0.5)
            """

    def _intro_message(self, enemy, is_boss_room):
        if is_boss_room:
            logger.info(f"Boss Enconter: {enemy.name}")
            print(f"\n{Colors.RED}{Colors.BOLD}╔══════════════════════════════════════════╗")
            print(f"║              BOSS ENCOUNTER              ║")
            print(f"╚══════════════════════════════════════════╝{Colors.RESET}")
            typewriter_effect(f"\n{Colors.RED}{Colors.BOLD}The {enemy.name} emerges from the shadows!{Colors.RESET}", 0.03 * config.game_speed_multiplier)
            sleep(1)
        else:
            logger.info(f"Enemy enconter: {enemy.name}")
            print(f"\n{Colors.RED}A {enemy.name} appears!{Colors.RESET}")
            sleep(0.5)

    def _auto_heal_rest(self, player: Player):
        if player.stats.hp < player.stats.max_hp / 2:
            typewriter_effect(f"\n[Assistant]: {Colors.RED}You are low on health, be carful.{Colors.RESET}", 0.03 * config.game_speed_multiplier)
            typewriter_effect(f"[Assistant]: {Colors.BLUE}Requesting permission..{Colors.RESET}", 0.05 * config.game_speed_multiplier)
            loading(2)
            typewriter_effect(f"[Assistant]: {Colors.GREEN}Permission allowed, executing command...{Colors.RESET}\n", 0.03 * config.game_speed_multiplier)
            sleep(1)
            execute_command("player.heal(999)", allowed=True, prnt=True, context={"player": player})
            sleep(0.5)
            typewriter_effect(f"\n[Assistant]: {Colors.GREEN}Player healed successfully..{Colors.RESET}", 0.03 * config.game_speed_multiplier)
        if player.stats.stamina < player.stats.max_stamina / 2:
            typewriter_effect(f"\n[Assistant]: {Colors.RED}You seem exausted.{Colors.RESET}", 0.03 * config.game_speed_multiplier)
            typewriter_effect(f"[Assistant]: {Colors.BLUE}Requesting permission..{Colors.RESET}", 0.05 * config.game_speed_multiplier)
            loading(2)
            typewriter_effect(f"[Assistant]: {Colors.GREEN}Permission allowed, executing command...{Colors.RESET}\n", 0.03 * config.game_speed_multiplier)
            sleep(1)
            execute_command("player.rest_stamina(999)", allowed=True, prnt=True, context={"player": player})
            sleep(0.5)
            typewriter_effect(f"\n[Assistant]: {Colors.GREEN}Player rested successfully...{Colors.RESET}", 0.03 * config.game_speed_multiplier)
      


    # ----- Inventaire -----

    def on_item_use(self, player, item):
        """Hook called when player uses an item."""
        pass

    def has_inventory_limit(self) -> bool:
        """Return True if this mode limits inventory size."""
        return False

    def get_inventory_limit(self) -> int | None:
        """Return the inventory limit if any. Returns int or None."""
        return None


    # ----- Progression -----

    def on_level_up(self, player):
        """Hook called when player levels up."""
        pass

    def level_up_bonus(self):
        return {
            "hp": 10,
            "mana": 5,
            "stamina": 5,
            "attack": 2,
            "defense": 2,
            "agility": 1
        }
    
    def get_ng_plus(self, player) -> int:
        return player.ng_plus[self.name]
    

    # ----- Exploration -----

    def get_room_count(self):
        # Valeur par défaut
        return random.randint(5, 8)

    def maybe_trigger_event(self, player):
        if random.random() < 0.2:  # 20% de chance
            event = random.choice(EVENTS)
            event.trigger(player)
    

    # ----- Loot & Shop -----

    def get_available_rarities(self):
        return ["common", "uncommon", "rare", "epic", "legendary", "divine"]

    def get_rarity_boost(self):
        return 1.0
    
    def get_shop_item_num(self):
        return random.randint(5, 7)


class HardcoreMode(GameMode):
    def __init__(self):
        super().__init__("hardcore")

    def take_damage(self, player, damage):
        # Hardcore mode increases damage taken by 50%
        true_damage = int(damage * 1.5)
        player.stats.permanent_stats["hp"] = max(0, player.stats.permanent_stats["hp"] - true_damage)
        player.stats.hp = player.stats.permanent_stats["hp"]
        return true_damage

    def modify_damage_dealt(self, player, damage):
        # Hardcore mode reduces damage dealt by 20%
        return int(damage * 0.8)

    def modify_damage_taken(self, player, damage):
        # Hardcore mode increases damage taken by 50%
        return int(damage * 1.5)

    def has_inventory_limit(self) -> bool:
        return True

    def get_inventory_limit(self) -> int | None:
        return 20  # Smaller inventory limit for hardcore mode

    def level_up_bonus(self):
        return {
            "hp": 3,
            "mana": 2,
            "stamina": 2,
            "attack": 1,
            "defense": 1,
            "agility": 0
        }

    def get_shop_item_num(self):
        return random.randint(1, 3)

    def get_room_count(self):
        return random.randint(10, 15)

    def get_available_rarities(self):
        return ["common", "uncommon", "rare"]

    def get_rarity_boost(self):
        return 0.8


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

    def get_room_count(self):
        return random.randint(6, 10)

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

    def get_inventory_limit(self) -> int | None:
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

class PuzzleMode(GameMode):
    def __init__(self):
        super().__init__("puzzle")

    def take_damage(self, player, damage):
        # Puzzle mode reduces damage taken by 30%
        true_damage = int(damage * 0.7)
        player.stats.permanent_stats["hp"] = max(0, player.stats.permanent_stats["hp"] - true_damage)
        player.stats.hp = player.stats.permanent_stats["hp"]
        return true_damage

    def modify_damage_dealt(self, player, damage):
        # Puzzle mode increases damage dealt by 10%
        return int(damage * 1.1)

    def modify_damage_taken(self, player, damage):
        # Puzzle mode reduces damage taken by 30%
        return int(damage * 0.7)

    def level_up_bonus(self):
        return {
            "hp": 8,
            "mana": 6,
            "stamina": 6,
            "attack": 2,
            "defense": 2,
            "agility": 1
        }

    def get_room_count(self):
        return random.randint(5, 7)

    def get_available_rarities(self):
        return ["common", "uncommon", "rare", "epic", "legendary", "divine", "???"]

    def get_rarity_boost(self):
        return 1.1

    def get_shop_item_num(self):
        return random.randint(3, 5)

