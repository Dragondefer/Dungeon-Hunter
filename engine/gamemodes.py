__version__ = "5.0"
__creation__ = "08-03-2026"

# Dungeon Hunter - Game Mode Architecture
# (c) Dragondefer 2025
# Licensed under CC BY-NC 4.0

from abc import ABC, abstractmethod
from typing import Optional, cast
import random
import time
from interface.colors import Colors
from engine.game_utility import (clear_screen, game_over, choose_difficulty,
                                 handle_error, interactive_bar, loading,
                                 move_cursor, get_input)
from engine.dungeon import Room, Dungeon, generate_dungeon 
from engine.logger import logger
from core.entity import Player
from data import get_random_names, quests_dict
from config import agent_is_enabled, get_agent
from engine.difficulty import RealisticDifficulty


class BaseGameMode(ABC):
    """
    Abstract base class for all game modes.
    Provides a common interface and initialization pattern for different gameplay modes.
    """
    
    def __init__(self, player: Optional[Player], dev_mode: bool = False, debug: int = 0) -> None:
        """
        Initialize a game mode.
        
        Args:
            player: The player object (if continuing from another mode)
            dev_mode: Developer mode flag
            debug: Debug level
        """
        self.player: Optional[Player] = player
        self.dev_mode: bool = dev_mode
        self.debug: int = debug
        self.mode_running: bool = True
    
    @abstractmethod
    def run(self):
        """Main loop for this game mode. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup and save state when exiting the mode. Must be implemented by subclasses."""
        pass


class DungeonMode(BaseGameMode):
    """
    GameMode for dungeon exploration and main gameplay loop.
    Contains all logic for exploration, inventory, resting, combat, and dungeon progression.
    """
    
    def __init__(self, continue_game: bool = False, loaded_player: Optional[Player] = None, dev_mode: bool = False, debug: int = 0) -> None:
        """
        Initialize the DungeonMode.
        
        Args:
            continue_game: Whether to continue from a saved game
            loaded_player: The loaded player object if continuing
            dev_mode: Developer mode flag
            debug: Debug level
        """
        # Initialize player - ensure it's always a Player instance
        if continue_game and loaded_player is not None:
            player: Player = loaded_player
        else:
            # New game
            name = get_input(f"\n{Colors.CYAN}Enter your name, brave adventurer: {Colors.RESET}")
            player = Player(name if name else get_random_names())
            choose_difficulty(player)
            
            # Give player a starting quest
            starting_quest = quests_dict.get("Dungeon Explorer")
            if starting_quest:
                player.quests.append(starting_quest)
        
        # Call parent constructor
        super().__init__(player=player, dev_mode=dev_mode, debug=debug)
        
        # Type guard: ensure player is not None and cast to Player
        assert self.player is not None, "Player must be initialized"
        # For type checking: DungeonMode always has a player, cast here once
        self.player: Player = cast(Player, self.player)  # type: ignore[assignment]
        
        # Game state variables
        self.game_running: bool = True
        self.end: bool = False
        self.player_survived: bool = True
        
        # Initialize dungeon
        self.dungeon: Dungeon = Dungeon()
        self.dungeon.extend(generate_dungeon(player=self.player))
    
    def run(self):
        """Main gameplay loop for DungeonMode."""
        # Type narrowing for mypy/pylance
        player: Player = cast(Player, self.player)
        
        while self.game_running and player.is_alive():
            if self.debug >= 1:
                get_input()
            clear_screen()

            player.display_dungeon_level(player.current_room_number)
            move_cursor(0, 0)
            player.display_status()
            
            print(f"\n{Colors.YELLOW}What would you like to do?{Colors.RESET}")
            print(f"{Colors.CYAN}1. Explore a new room{Colors.RESET}")
            print(f"{Colors.GREEN}2. Check inventory{Colors.RESET}")
            print(f"{Colors.RED}3. Rest{Colors.RESET}")
            print(f"{Colors.MAGENTA}4. Information submenu{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}5. Save game{Colors.RESET}")
            print(f"{Colors.BRIGHT_BLACK}6. Settings{Colors.RESET}\n")
            
            # Use get_input instead of input to allow agent control if enabled
            choice = get_input(f"{Colors.CYAN}Your choice: {Colors.RESET}", options=["1","2","3"], player=self.player, use_agent=agent_is_enabled())
            logger.info(f"Player choice: {choice}")
            
            if choice == "1":  # Explore a new room
                self._handle_exploration()
        
            elif choice == "2":  # Check inventory / ressources
                self._handle_inventory()

            elif choice == "3":  # Rest
                self._handle_rest()

            elif choice == "4":  # Information submenu
                self._handle_information_submenu()

            elif choice == "5":  # Save game
                self._handle_save()
            
            elif choice == "6":  # Settings submenu
                self._handle_settings()
            
            elif choice == "dev" and self.dev_mode == True:  # activate dev debug test
                self._handle_dev_mode()

            else:
                # Mode développeur : exécute une commande Python
                if self.dev_mode and choice.startswith("!"):
                    try:
                        result = eval(choice[1:], globals(), locals())
                        if result is not None:
                            print(result)
                            get_input()
                    except Exception as e:
                        print(f"[ERROR] {e}")
                        get_input()
                    continue
                print(f"{Colors.RED}Invalid choice. Try again.{Colors.RESET}")
                time.sleep(1)
        
        if not self.player.is_alive() and self.end == False:
            game_over("died in battle")
            self.end = True
    
    def cleanup(self):
        """Cleanup and save state when exiting DungeonMode."""
        try:
            self.player.save_player("auto_save")
            agent = get_agent()
            if agent:
                agent.save_q_table("ai/q_table.json")
            logger.info("DungeonMode cleanup: Game saved successfully.")
        except Exception as e:
            logger.warning(f"DungeonMode cleanup error: {e}")
    
    def _handle_exploration(self):
        """Handle room exploration logic."""
        if not self.dungeon:
            if not self.player_survived or not self.player.is_alive():
                game_over("died in battle")
                self.game_running = False
                self.end = True
                return
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}Congratulations! You've cleared dungeon level {self.player.dungeon_level}!{Colors.RESET}")
            logger.info(f"Player cleared dungeon level {self.player.dungeon_level}")
            self.player.dungeon_level += 1

            # After finishing level 10 dungeon for the first time
            if self.player.dungeon_level == 11 and self.player.ng_plus.get(str(self.player.difficulty), 0) == 0:
                print(f"\n{Colors.BRIGHT_YELLOW}You have finished level 10 dungeon!{Colors.RESET}")
                
                # Unlock the two difficulty:
                self.player.finished_difficulties["normal"] = True
                self.player.unlocked_difficulties["soul_enjoyer"] = True
                self.player.unlocked_difficulties["realistic"] = True

                print(f"\n{Colors.BRIGHT_YELLOW}You can now change difficulty or start a new game + (NG+).{Colors.RESET}")
                choice = get_input(f"\n{Colors.YELLOW}Do you want to change difficulty ? (y/n): {Colors.RESET}", options=["y","n"], player=self.player, use_agent=agent_is_enabled()).lower()
                if choice == "y":
                    print(f"\n{Colors.YELLOW}You can now choose a new difficulty level.{Colors.RESET}")
                    self.player.difficulty = choose_difficulty(self.player)
                    print(f"\n{Colors.YELLOW}You have chosen {self.player.difficulty} difficulty.{Colors.RESET}")
                else:
                    print(f"\n{Colors.YELLOW}You have chosen to make a new game +.{Colors.RESET}")
                    print(f"\n{Colors.YELLOW}Generating a new dungeon...{Colors.RESET}")
                    time.sleep(2)
                    self.player.ng_plus[str(self.player.difficulty)] += 1
                self.player.dungeon_level = 1
                self.player.current_room_number = 0
            
            if self.debug >= 1:
                print(Colors.BLUE, 'DEBUG: No dungeon, generating a new dungeon...', Colors.RESET)

            dungeon_rooms = generate_dungeon(player=self.player)
            self.dungeon = Dungeon()
            self.dungeon.extend(dungeon_rooms)
            
            # Update quest progress for complete_dungeon_levels
            for quest in self.player.quests:
                if quest.objective_type == "complete_dungeon_levels" and not quest.completed:
                    if quest.update_progress():
                        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")

            if self.debug >= 1:
                print(self.player.difficulty)
            
            # Reward player for clearing a dungeon level
            self.player.heal(self.player.stats.max_hp // 4)
            self.player.rest_stamina(100)
            self.player.regen_mana(25)
            level_reward = self.player.dungeon_level * 50
            print(f"{Colors.YELLOW}You receive {level_reward} gold for clearing the dungeon!{Colors.RESET}")
            self.player.gold += level_reward
            self.player.gain_xp(self.player.dungeon_level * 50)

            self.player.current_room_number = 0
            
            time.sleep(0.5)
            get_input(f"\n{Colors.YELLOW}Press Enter to continue to dungeon level {self.player.dungeon_level}...{Colors.RESET}")
        else:
            if self.debug >= 1:
                print(f"{Colors.CYAN}DEBUG: Dungeon size before exploration: {len(self.dungeon)}{Colors.RESET}")
            room = self.dungeon.pop(0)
            self.player_survived = room.enter(self.player)
            self.player.current_room_number += 1
            self.player.total_rooms_explored += 1
            
            # Update quest progress if applicable
            for quest in self.player.quests:
                if quest.objective_type == "explore_rooms" and not quest.completed:
                    if quest.update_progress():
                        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
                elif quest.objective_type == "collect_gold" and not quest.completed:
                    if self.player.gold >= quest.objective_amount:
                        quest.completed = True
                        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
                        print(f"{Colors.YELLOW}Rewards: {quest.reward_gold} gold, {quest.reward_xp} XP{Colors.RESET}")
                        self.player.gold += quest.reward_gold
                        self.player.gain_xp(quest.reward_xp)
                        
                        if quest.reward_item:
                            self.player.inventory.append(quest.reward_item)
                            print(f"{Colors.GREEN}You received: {quest.reward_item.name}{Colors.RESET}")
                        
                        self.player.quests.remove(quest)
                        self.player.completed_quests.append(quest)
            
            if not self.player_survived or not self.player.is_alive() and self.end == False:
                # Instead of game over and stopping the game, reset the player and dungeon to respawn
                game_over("died in battle")
                print(f"\n{Colors.RED}You have died! Respawning...{Colors.RESET}")
                self.player.reset_player()
                self.dungeon = Dungeon()
                self.dungeon.extend(generate_dungeon(player=self.player))
                self.game_running = True
                self.end = False
                self.player.current_room_number = 0
                self.player.total_rooms_explored = 0
                time.sleep(2)
                return
            
            time.sleep(0.5)
            get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _handle_inventory(self):
        """Handle inventory and resources management."""
        choice = get_input(f"\n{Colors.YELLOW}{Colors.GREEN}1. Manage Inventory\n{Colors.BRIGHT_BLUE}2. View Resources\n\n{Colors.CYAN}Your choice: {Colors.RESET}", options=["1","2"], player=self.player, use_agent=agent_is_enabled()) if isinstance(self.player.difficulty, RealisticDifficulty) else "1"

        if choice == "1":
            self.player.manage_inventory()
        elif choice == "2":
            self.player.display_resources()
    
    def _handle_rest(self):
        """Handle resting and stamina recovery."""
        amount = interactive_bar(0, self.player.stats.permanent_stats["max_hp"] - self.player.stats.permanent_stats["hp"], 10, False, 10, Colors.GREEN, 50)
        if self.player.gold >= amount:
            old_hp = self.player.stats.hp
            old_stamina = self.player.stats.stamina
            self.player.heal(amount)
            self.player.rest_stamina(amount)
            loading(amount // 10)
            print(f"\n{Colors.GREEN}You rest for a while and recover:\n{self.player.stats.hp - old_hp} HP,\n{self.player.stats.stamina - old_stamina} Stamina.{Colors.RESET}")
            time.sleep(0.1)
            # Chance of being robbed by a goblin:
            if self.player.difficulty == "Normal":
                amount = random.randint(int(amount * 0.8), int(amount * 1.2))
            else:
                amount = random.randint(int(amount * 1), int(amount * 1.5))
            
            self.player.gold = max(0, self.player.gold - amount)
            if amount > 0:
                print(f"\n{Colors.RED}A goblin stole {amount} gold while you were resting!{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}You don't have enough gold to rest.{Colors.RESET}")
        time.sleep(0.1)

        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _handle_information_submenu(self):
        """Handle information submenu (stats, logbook, quests, achievements)."""
        while True:
            clear_screen()
            print(f"\n{Colors.YELLOW}{Colors.UNDERLINE}Information Submenu{Colors.RESET}")
            print(f"{Colors.CYAN}1. View Player Stats{Colors.RESET}")
            print(f"{Colors.MAGENTA}2. View Logbook{Colors.RESET}")
            print(f"{Colors.GREEN}3. View Quests{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}4. View Achievements{Colors.RESET}")
            print(f"{Colors.RED}5. Back to Main Menu{Colors.RESET}")

            choice = get_input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}")

            if choice == "1":  # View Player Stats
                self.player.display_stats_summary()

            elif choice == "2":  # View Logbook
                self.player.display_logbook()
            
            elif choice == "3":  # View Quests
                self.player.view_quests()

            elif choice == "4":  # View Achievements
                self.player.display_achievements()

            elif choice == "5":  # Back to Main Menu
                break
    
    def _handle_save(self):
        """Handle game saving and analytics."""
        # Ask the save name:
        save_name = get_input(f"\n{Colors.YELLOW}Enter a save name: {Colors.RESET}")
        self.player.save_player(save_name)
        # Save agent Q-table if agent is enabled
        agent = get_agent()
        if agent:
            agent.save_q_table("ai/q_table.json")
        time.sleep(0.5)

        # Nicely formatted question to ask player for analytics consent
        print(f"\n{Colors.BRIGHT_CYAN}Would you like to send anonymous analytics to help improve the game?{Colors.RESET}")
        print(f"{Colors.CYAN}This data includes your playtime, levels completed, rooms explored, and more.")
        print(f"It is completely anonymous and cannot be traced back to you.")
        print(f"Your contribution helps us make Dungeon Hunter better for everyone!")
        print(f"See global analytics here: https://dragondefer.github.io/Dungeon-Hunter/analytics/analytics.html\n{Colors.RESET}")

        # Not implemented yet
        # consent = get_input(f"{Colors.BRIGHT_YELLOW}Send analytics? (y/n): {Colors.RESET}").lower()
        consent = "n"
        if consent == 'y':
            from data.player_data import change_analytics
            change_analytics(True)
            print(f"{Colors.GREEN}Thank you for contributing to the analytics!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Analytics not sent. You can send them later from the main menu.{Colors.RESET}")

        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _handle_settings(self):
        """Handle settings submenu."""
        while True:
            clear_screen()
            print(f"\n{Colors.YELLOW}{Colors.UNDERLINE}Settings Submenu{Colors.RESET}")
            print(f"{Colors.BRIGHT_RED}1. Continue{Colors.RESET}")
            print(f"{Colors.CYAN}2. Change game speed{Colors.RESET}")
            print(f"{Colors.RED}3. Quit game{Colors.RESET}")

            setting_choice = get_input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}")

            if setting_choice == "1":
                break

            elif setting_choice == "2":
                print(f"{Colors.GREEN}Option 1 selected.{Colors.RESET}")
                # Implement game speed change submenu
                from engine.game_utility import game_speed_settings
                game_speed_settings()
                
            elif setting_choice == "3": # Quit game
                confirm = get_input(f"{Colors.RED}Are you sure you want to quit? (y/n): {Colors.RESET}").lower()
                if confirm == "y":
                    try:
                        self.player.save_player("auto_save")
                        # Save agent Q-table if agent is enabled
                        agent = get_agent()
                        if agent:
                            agent.save_q_table("ai/q_table.json")
                    except Exception as e:
                        handle_error()
                        print(f"{Colors.RED}Error saving auto-save: {e}{Colors.RESET}")
                    self.game_running = False
                    
            else:
                print(f"{Colors.RED}Invalid choice. Try again.{Colors.RESET}")
                time.sleep(1)
    
    def _handle_dev_mode(self):
        """Handle developer mode menu."""
        print(Colors.gradient_text('dev mode activated', (0, 0, 255), (0, 255, 0)))
        debug_dungeon = Dungeon(self.dungeon) if isinstance(self.dungeon, list) else self.dungeon
        from engine.dev_mod import debug_menu
        debug_menu(self.player, debug_dungeon)


# ==============================================
# ADDITIONAL GAME MODE TEMPLATES
# ==============================================

class ShopMode(BaseGameMode):
    """
    GameMode for shopping and item trading.
    Players can buy and sell items, manage inventory, and interact with merchants.
    
    TODO: Implement shop inventory system
    TODO: Implement merchant dialogue
    TODO: Implement item pricing and trading logic
    """
    
    def __init__(self, player: Player, dev_mode: bool = False, debug: int = 0) -> None:
        """Initialize ShopMode with player reference."""
        super().__init__(player=player, dev_mode=dev_mode, debug=debug)
        self.shop_inventory: list = []  # Items available for purchase
        self.merchant_name: str = "Merchant"
    
    def run(self) -> None:
        """Main loop for ShopMode."""
        self.mode_running = True
        while self.mode_running and self.player and self.player.is_alive():
            clear_screen()
            print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}Welcome to the {self.merchant_name}'s Shop!{Colors.RESET}")
            print(f"{Colors.CYAN}1. Browse Items{Colors.RESET}")
            print(f"{Colors.GREEN}2. Sell Items{Colors.RESET}")
            print(f"{Colors.RED}3. Leave Shop{Colors.RESET}")
            
            choice = get_input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}")
            
            if choice == "1":
                self._browse_items()
            elif choice == "2":
                self._sell_items()
            elif choice == "3":
                self.mode_running = False
            else:
                print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                time.sleep(1)
    
    def _browse_items(self) -> None:
        """Display and allow purchase of items."""
        print(f"\n{Colors.YELLOW}Available items:{Colors.RESET}")
        # TODO: Implement shop item browsing
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _sell_items(self) -> None:
        """Display player inventory and allow selling items."""
        print(f"\n{Colors.YELLOW}Your items for sale:{Colors.RESET}")
        # TODO: Implement item selling
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def cleanup(self):
        """Cleanup when exiting ShopMode."""
        logger.info("ShopMode cleanup completed.")


class ArenaMode(BaseGameMode):
    """
    GameMode for combat arena/training.
    Players can engage in optional combat with selected enemies for rewards.
    
    TODO: Implement arena enemy selection
    TODO: Implement arena combat system
    TODO: Implement arena reward system
    """
    
    def __init__(self, player: Player, dev_mode: bool = False, debug: int = 0) -> None:
        """Initialize ArenaMode with player reference."""
        super().__init__(player=player, dev_mode=dev_mode, debug=debug)
        self.arena_difficulty: str = "Normal"
        self.selected_enemy: Optional[object] = None
    
    def run(self) -> None:
        """Main loop for ArenaMode."""
        self.mode_running = True
        while self.mode_running and self.player and self.player.is_alive():
            clear_screen()
            print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}Welcome to the Arena!{Colors.RESET}")
            print(f"{Colors.CYAN}1. Fight an Enemy{Colors.RESET}")
            print(f"{Colors.GREEN}2. View Arena Rules{Colors.RESET}")
            print(f"{Colors.YELLOW}3. Check Leaderboard{Colors.RESET}")
            print(f"{Colors.RED}4. Leave Arena{Colors.RESET}")
            
            choice = get_input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}")
            
            if choice == "1":
                self._start_combat()
            elif choice == "2":
                self._show_rules()
            elif choice == "3":
                self._show_leaderboard()
            elif choice == "4":
                self.mode_running = False
            else:
                print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                time.sleep(1)
    
    def _start_combat(self):
        """Initiate arena combat."""
        print(f"\n{Colors.YELLOW}Preparing for combat...{Colors.RESET}")
        # TODO: Implement arena combat
        time.sleep(1)
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _show_rules(self):
        """Display arena rules."""
        print(f"\n{Colors.CYAN}{Colors.BOLD}Arena Rules:{Colors.RESET}")
        print(f"{Colors.YELLOW}1. All combats are voluntary{Colors.RESET}")
        print(f"{Colors.YELLOW}2. Victory grants additional rewards{Colors.RESET}")
        print(f"{Colors.YELLOW}3. Defeat does not result in character death{Colors.RESET}")
        # TODO: Add more rules
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _show_leaderboard(self):
        """Display arena leaderboard."""
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}Arena Leaderboard{Colors.RESET}")
        # TODO: Implement leaderboard system
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def cleanup(self):
        """Cleanup when exiting ArenaMode."""
        logger.info("ArenaMode cleanup completed.")


class RestingMode(BaseGameMode):
    """
    GameMode for peaceful resting and meditation between dungeons.
    Players can fully recover, meditate, and prepare for challenges ahead.
    
    TODO: Implement extended resting mechanics
    TODO: Implement meditation system with XP gains
    TODO: Implement dream sequences or story elements
    """
    
    def __init__(self, player: Player, dev_mode: bool = False, debug: int = 0) -> None:
        """Initialize RestingMode with player reference."""
        super().__init__(player=player, dev_mode=dev_mode, debug=debug)
        self.rest_duration: int = 0
    
    def run(self) -> None:
        """Main loop for RestingMode."""
        self.mode_running = True
        while self.mode_running and self.player and self.player.is_alive():
            clear_screen()
            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Peaceful Sanctuary{Colors.RESET}")
            print(f"{Colors.CYAN}1. Rest and Recovery{Colors.RESET}")
            print(f"{Colors.MAGENTA}2. Meditate{Colors.RESET}")
            print(f"{Colors.YELLOW}3. Prepare Supplies{Colors.RESET}")
            print(f"{Colors.RED}4. Leave Sanctuary{Colors.RESET}")
            
            choice = get_input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}")
            
            if choice == "1":
                self._full_recovery()
            elif choice == "2":
                self._meditate()
            elif choice == "3":
                self._prepare_supplies()
            elif choice == "4":
                self.mode_running = False
            else:
                print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                time.sleep(1)
    
    def _full_recovery(self):
        """Fully recover all player stats."""
        print(f"\n{Colors.GREEN}You rest deeply and recover completely...{Colors.RESET}")
        # TODO: Implement full recovery
        time.sleep(1)
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _meditate(self):
        """Meditate for bonus XP and mental clarity."""
        print(f"\n{Colors.MAGENTA}You enter a meditative state...{Colors.RESET}")
        # TODO: Implement meditation with XP gains
        time.sleep(1)
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def _prepare_supplies(self):
        """Prepare supplies for upcoming challenges."""
        print(f"\n{Colors.YELLOW}Preparing supplies for the journey ahead...{Colors.RESET}")
        # TODO: Implement supply crafting/preparation
        time.sleep(1)
        get_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    
    def cleanup(self):
        """Cleanup when exiting RestingMode."""
        logger.info("RestingMode cleanup completed.")


class StoryMode(BaseGameMode):
    """
    GameMode for story sequences and narrative cutscenes.
    Players experience story progression, dialogue, and character interactions.
    
    TODO: Implement dialogue system
    TODO: Implement choice trees
    TODO: Implement story progression tracking
    """
    
    def __init__(self, player: Player, story_id: str = "default", dev_mode: bool = False, debug: int = 0) -> None:
        """Initialize StoryMode with player reference and story identifier."""
        super().__init__(player=player, dev_mode=dev_mode, debug=debug)
        self.story_id: str = story_id
        self.current_scene: int = 0
        self.story_scenes: list = []  # List of story scenes
    
    def run(self):
        """Main loop for StoryMode."""
        self.mode_running = True
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}Story Sequence{Colors.RESET}")
        # TODO: Implement story scene progression
        print(f"{Colors.YELLOW}Story mode loading...[Not yet implemented]{Colors.RESET}")
        time.sleep(1)
        self.mode_running = False
    
    def _load_story(self):
        """Load story scenes from story data."""
        # TODO: Implement story loading from data files
        pass
    
    def _display_scene(self):
        """Display current story scene."""
        # TODO: Implement scene display with dialogue and choices
        pass
    
    def _handle_choice(self, choice):
        """Handle player choice in story."""
        # TODO: Implement choice handling and branching
        pass
    
    def cleanup(self):
        """Cleanup when exiting StoryMode."""
        logger.info("StoryMode cleanup completed.")


class GameModeManager:
    """
    Manager for switching between different game modes.
    Handles state preservation and transitions between modes.
    
    Usage:
        manager = GameModeManager(player, dev_mode, debug)
        manager.switch_to_mode("dungeon")
        manager.switch_to_mode("shop")
    """
    
    def __init__(self, player: Player, dev_mode: bool = False, debug: int = 0) -> None:
        """Initialize GameModeManager."""
        self.player: Player = player
        self.dev_mode: bool = dev_mode
        self.debug: int = debug
        self.current_mode: Optional[BaseGameMode] = None
        self.mode_history: list = []
        
        # Registry of available modes
        self.modes: dict = {
            "dungeon": DungeonMode,
            "shop": ShopMode,
            "arena": ArenaMode,
            "resting": RestingMode,
            "story": StoryMode,
        }
    
    def switch_to_mode(self, mode_name: str, **kwargs) -> bool:
        """
        Switch to a different game mode.
        
        Args:
            mode_name: Name of the mode to switch to (must be in self.modes)
            **kwargs: Additional arguments to pass to the mode constructor
        """
        if self.current_mode:
            # Cleanup previous mode
            self.current_mode.cleanup()
            self.mode_history.append(self.current_mode)
        
        if mode_name not in self.modes:
            logger.warning(f"Mode '{mode_name}' not found in registry.")
            return False
        
        try:
            mode_class = self.modes[mode_name]
            if mode_name == "dungeon":
                # DungeonMode has special initialization
                self.current_mode = mode_class(
                    continue_game=False,
                    loaded_player=self.player,
                    dev_mode=self.dev_mode,
                    debug=self.debug
                )
            else:
                self.current_mode = mode_class(
                    player=self.player,
                    dev_mode=self.dev_mode,
                    debug=self.debug,
                    **kwargs
                )
            logger.info(f"Switched to mode: {mode_name}")
            return True
        except Exception as e:
            logger.error(f"Error switching to mode '{mode_name}': {e}")
            return False
    
    def run_current_mode(self) -> None:
        """Run the current game mode."""
        if self.current_mode:
            self.current_mode.run()
        else:
            logger.warning("No mode is currently active.")
    
    def get_current_mode_name(self) -> Optional[str]:
        """Get the name of the current mode."""
        if self.current_mode:
            return type(self.current_mode).__name__
        return None
