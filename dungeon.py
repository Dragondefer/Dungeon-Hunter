__version__ = "1050.0"
__creation__ = "09-03-2025"

import time
import random

from game_utility import (clear_screen, typewriter_effect,
                          dice_animation, handle_error,
                          timed_input_pattern)
from colors import Colors
from entity import Player, generate_enemy, load_player
from items import Armor, Weapon, Potion, generate_random_item
from data import room_descriptions, puzzle_choices, rest_events
from logger import logger

debug = 0

# Beware: Rooms may hide secrets that trap your soul forever.
class Room:
    """
    Represents a room within the dungeon, encapsulating various gameplay elements and interactions.

    Attributes:
        room_type (str): Specifies the category of the room, such as "combat", "treasure", "shop", "rest", "puzzle", or "boss".
        description (str): A textual description providing details about the room's appearance or ambiance.
        enemies (list[Enemy]): A list containing enemy instances present in the room, if any.
        items (list[Item]): A list of items available within the room for the player to collect.
        trap (dict | None): Optional trap details that may trigger upon player entry, including type, effect, and status.
        visited (bool): Indicates whether the player has previously entered this room, affecting interaction behavior.

    Methods:
        enter(player: Player) -> bool:
            Manages the player's entry into the room, including displaying descriptions, triggering traps, and handling room-specific events.

        trigger_trap(player: Player) -> None:
            Activates the trap mechanism if present and applies its effects to the player.

        handle_room(player: Player) -> bool:
            Directs the flow to the appropriate handler based on the room type, such as combat, treasure, shop, rest, boss, or puzzle.

        handle_combat(player: Player, is_boss_room: bool = False) -> bool:
            Conducts combat sequences with enemies in the room, including boss encounters.

        handle_treasure(player: Player) -> bool:
            Facilitates the collection of treasure items by the player.

        handle_shop(player: Player) -> bool:
            Opens the shop interface for buying and selling items.

        sell_items(player: Player, shopkeeper: str) -> None:
            Allows the player to sell items to the shopkeeper.

        handle_rest(player: Player) -> bool:
            Allows the player to rest, recover, and manage inventory.

        random_rest_event(player: Player) -> None:
            Triggers a random event during rest that can affect player stats or inventory.

        handle_puzzle(player: Player) -> bool:
            Manages puzzle interactions and challenges within the room.

        handle_riddle(player: Player) -> bool:
            Handles riddle-type puzzles.

        handle_number_puzzle(player: Player) -> bool:
            Handles number-guessing puzzles.

        handle_sequence_puzzle(player: Player) -> bool:
            Handles mathematical sequence puzzles.

        handle_choice_puzzle(player: Player) -> bool:
            Manages choice-based puzzles where the player selects from options.

        handle_dice_puzzle(player: Player) -> bool:
            Manages dice roll puzzles with rewards based on outcomes.
    """
    def __init__(self, room_type, description, enemies=None, items=None, trap=None):
        self.available_room_type = ["combat", "treasure", "shop", "rest", "puzzle"] # and "boss"
        self.room_type = room_type  # "combat", "treasure", "shop", "rest", "boss", "puzzle", etc.
        self.description = description
        self.enemies = enemies or []
        self.items = items or []
        self.trap = trap
        self.visited = False
    
    def enter(self, player):
        global debug
        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Entering room of type '{self.room_type}' with description: {self.description}{Colors.RESET}")
        logger.info(f"Player entering room of type '{self.room_type}' with description: {self.description}")
        if not self.visited:
            
            splited_desc = self.description.split('\n') if '\n' in self.description else [self.description]

            for i, desc_part in enumerate(splited_desc):
                if i > 0:  # Ajoute une pause uniquement après la première ligne
                    input()
                typewriter_effect(f"{Colors.CYAN}{desc_part}{Colors.RESET}", 0.02, end='')
            self.visited = True
        else:
            print(f"\n{Colors.CYAN}You've returned to {self.description}{Colors.RESET}")
            logger.info(f"Player returned to room: {self.description}")
        
        if self.trap and not self.trap["triggered"]:
            logger.warning(f"Trap triggered in room: {self.description} - Trap details: {self.trap}")
            self.trigger_trap(player)
            
        return self.handle_room(player)
    
    def trigger_trap(self, player):
        print(f"\n{Colors.RED}{Colors.BOLD}*CLICK*{Colors.RESET}")
        player.traps_triggered +=1
        logger.info(f"Trap activated: {self.trap['description']}")
        time.sleep(0.5)
        print(f"{Colors.RED}It's a trap! {self.trap['description']}{Colors.RESET}")
        
        # Give player a chance to avoid the trap based on luck
        if random.random() < (0.1 + player.stats.luck * 0.01 + player.stats.agility * 0.01):
            print(f"{Colors.GREEN}Thanks to your quick reflexes, you manage to avoid the trap!{Colors.RESET}")
            logger.info("Player avoided the trap due to quick reflexes.")
        else:
            if self.trap["type"] == "damage":
                damage = self.trap["value"]
                player.stats.modify_stat(stat_name="hp", value=-damage)
                logger.info(f"Player took {damage} damage from trap.")
                #player.stats.hp = max(0, player.stats.hp - damage)
                print(f"{Colors.RED}You take {damage} damage from the trap!{Colors.RESET}")
            elif self.trap["type"] == "stat_reduction":
                stat = self.trap["stat"]
                value = self.trap["value"]
                if stat == "attack":
                    player.stats.modify_stat(stat_name="attack", value=-value, permanent=False)
                    logger.info(f"Player's attack temporarily reduced by {value} due to trap.")
                    print(f"{Colors.RED}Your attack is temporary reduced by {value}!{Colors.RESET}")
                elif stat == "defense":
                    player.stats.modify_stat(stat_name="defense", value=-value, permanent=False)
                    logger.info(f"Player's defense temporarily reduced by {value} due to trap.")
                    print(f"{Colors.RED}Your defense is temporary reduced by {value}!{Colors.RESET}")
        
        self.trap["triggered"] = True
    
    def handle_room(self, player):
        global debug

        if debug >= 1:
            print(f"\n{Colors.YELLOW}DEBUG: Entering handle_room() for \"{self.room_type}\"{Colors.RESET}")
        logger.debug(f"handle_room() called for room type \"{self.room_type}\"")
        if self.room_type == "combat":
            if debug >= 1:
                print(f"{Colors.RED}DEBUG: Combat room detected!{Colors.RESET}")
            logger.info("Combat room detected.")
            return self.handle_combat(player)
        elif self.room_type == "treasure":
            if debug >= 1:
                print(f"{Colors.GREEN}DEBUG: Treasure room detected!{Colors.RESET}")
            logger.info("Treasure room detected.")
            return self.handle_treasure(player)
        elif self.room_type == "shop":
            if debug >= 1:
                print(f"{Colors.CYAN}DEBUG: Shop room detected!{Colors.RESET}")
            logger.info("Shop room detected.")
            return self.handle_shop(player)
        elif self.room_type == "rest":
            if debug >= 1:
                print(f"{Colors.BLUE}DEBUG: Rest room detected!{Colors.RESET}")
            logger.info("Rest room detected.")
            return self.handle_rest(player)
        elif self.room_type == "boss":
            if debug >= 1:
                print(f"{Colors.RED}DEBUG: Boss room detected!{Colors.RESET}")
            logger.info("Boss room detected.")
            return self.handle_combat(player, True)
        elif self.room_type == "puzzle":
            if debug >= 1:
                print(f"{Colors.MAGENTA}DEBUG: Puzzle room detected!{Colors.RESET}")
            logger.info("Puzzle room detected.")
            return self.handle_puzzle(player)

        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Room type not triggering any event.{Colors.RESET}")
        logger.debug("Room type not triggering any event.")
        return True  # Continue exploration si rien ne se passe

    
    def handle_puzzle(self, player:Player):
        """Handles the puzzle room, allowing the player to solve various types of puzzles."""
        player.puzzles_solved += 1
        puzzle_types = ["riddle", "number", "sequence", "choice", "dice"]
        puzzle_type = random.choice(puzzle_types)
        
        logger.info(f"Player encountered a puzzle of type: {puzzle_type}")
        print(f"\n{Colors.CYAN}You encounter a puzzle.{Colors.RESET}")
        
        result = False
        if puzzle_type == "riddle":
            result = self.handle_riddle(player)
        elif puzzle_type == "number":
            result = self.handle_number_puzzle(player)
        elif puzzle_type == "sequence":
            result = self.handle_sequence_puzzle(player)
        elif puzzle_type == "choice":
            result = self.handle_choice_puzzle(player)
        elif puzzle_type == "dice":
            result = self.handle_dice_puzzle(player)
        
        if result:
            for quest in player.quests:
                if quest.objective_type == "complete_puzzles" and not quest.completed:
                    if quest.update_progress():
                        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
        return result
    
    def handle_number_puzzle(self, player):
        target = random.randint(1, 20)
        attempts = 5
        
        logger.info(f"Number puzzle target is {target} with {attempts} attempts allowed.")
        print(f"\n{Colors.CYAN}There's a strange mechanical device with numbered dials.{Colors.RESET}")
        print(f"{Colors.YELLOW}You need to guess the correct number between 1 and 20.{Colors.RESET}")
        print(f"{Colors.GREEN}The device will tell you if your guess is higher or lower than the target.{Colors.RESET}")
        
        for attempt in range(attempts):
            try:
                guess = int(input(f"\n{Colors.YELLOW}Your guess (attempt {attempt+1}/{attempts}): {Colors.RESET}"))
                logger.debug(f"Player guessed {guess} on attempt {attempt+1}")
                if guess == target:
                    print(f"\n{Colors.GREEN}Correct! The device whirs and opens.{Colors.RESET}")
                    
                    # Generate reward
                    gold_amount = random.randint(20, 50) * player.dungeon_level
                    player.gold += gold_amount
                    logger.info(f"Player guessed correctly and won {gold_amount} gold.")
                    print(f"{Colors.YELLOW}You found {gold_amount} gold!{Colors.RESET}")
                    
                    return True
                elif guess < target:
                    print(f"{Colors.BLUE}The target number is higher.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}The target number is lower.{Colors.RESET}")
            except ValueError:
                logger.warning("Player entered invalid input for number puzzle guess.")
                print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")
                attempt -= 1  # Don't count invalid inputs as attempts
        
        logger.info(f"Player failed to guess the number. The correct number was {target}.")
        print(f"\n{Colors.RED}You failed to guess the number. The correct number was {target}.{Colors.RESET}")
        print(f"{Colors.YELLOW}The device resets and nothing happens.{Colors.RESET}")
        
        return True


    def handle_riddle(self, player):
        """Managing a riddle."""
        riddles = [
            {"question": "I speak without a mouth and hear without ears. I have no one, but I live with the wind. Who am I?", "answer": "echo"},
            {"question": "The more you take, the more you leave behind. What am I?", "answer": "footprint"},
            {"question": "I have keys but no locks, a space but no room, and you can enter but you can't get out. What am I?", "answer": "keyboard"}
        ]

        riddle = random.choice(riddles)
        
        print(f"\n{Colors.MAGENTA}An ancient inscription reads:{Colors.RESET}")
        print(f"\"{Colors.CYAN}{riddle['question']}{Colors.RESET}\"")

        # Le joueur a 3 tentatives
        for attempt in range(3):
            answer = input(f"\n{Colors.YELLOW}Your response (attempt {attempt+1}/3) : {Colors.RESET}").lower().strip()

            if answer == riddle["answer"]:
                print(f"\n{Colors.GREEN}Correct! A secret passage opens up.{Colors.RESET}")
                player.gold += random.randint(50, 100)
                print(f"{Colors.YELLOW}You find a few gold!{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}Wrong answer! You're left with {2 - attempt} attempts.{Colors.RESET}")

        # Échec → Le joueur prend des dégâts
        print(f"\n{Colors.RED}You fail to solve the riddle. A trap is triggered !{Colors.RESET}")
        damage = random.randint(5, 15) * player.dungeon_level
        player.stats.hp = max(1, player.stats.hp - damage)  
        print(f"{Colors.RED}You suffer {damage} damage !{Colors.RESET}")

        return True
    
    
    def handle_dice_puzzle(self, player):
        print(f"\n{Colors.CYAN}You find a strange dice game set up on a table.{Colors.RESET}")
        print(f"{Colors.YELLOW}The rules state:{Colors.RESET}")
        print(f"{Colors.YELLOW}Roll three dice. If their sum is greater than 10, you win a prize.{Colors.RESET}")
        print(f"{Colors.YELLOW}However, if you roll three of the same number, you win a special prize!{Colors.RESET}")
        print(f"{Colors.YELLOW}It costs 10 gold to play.{Colors.RESET}")
        
        while True:
            while True:
                play = input(f"\n{Colors.CYAN}Do you want to play? (10 gold) [y/n]: {Colors.RESET}").lower()
                if play not in ['y', 'n']:
                    print(f"{Colors.RED}Invalid choice. Please enter 'y' or 'n'.{Colors.RESET}")
                    continue
                break
            if play == 'y':
                if player.gold < 10:
                    print(f"{Colors.RED}You don't have enough gold!{Colors.RESET}")
                    return True
                
                player.gold -= 10
                player.gold_spent += 10
                print(f"{Colors.YELLOW}You pay 10 gold to play.{Colors.RESET}")
                
                print(f"\n{Colors.CYAN}Rolling dice...{Colors.RESET}")
                dice1 = dice_animation()
                print(f"\n{Colors.YELLOW}You rolled: {dice1}{Colors.RESET}")
                time.sleep(0.5)
                dice2 = dice_animation()
                print(f"\n{Colors.YELLOW}You rolled: {dice2}{Colors.RESET}")
                time.sleep(0.5)
                dice3 = dice_animation()
                print(f"\n{Colors.YELLOW}You rolled: {dice3}{Colors.RESET}")
                time.sleep(0.5)

                total = dice1 + dice2 + dice3
                print(f"\n{Colors.YELLOW}You rolled: {dice1}, {dice2}, {dice3} (Total: {total}){Colors.RESET}")
                
                if dice1 == dice2 == dice3:
                    prize = generate_random_item(player=player)
                    player.inventory.append(prize)
                    print(f"\n{Colors.RAINBOW}JACKPOT! You won a special prize!{Colors.RESET}")
                    print(f"{Colors.GREEN}You received: {prize.name}!{Colors.RESET}")
                elif total > 10:
                    gold_won = random.randint(15, 30)
                    player.gold += gold_won
                    print(f"\n{Colors.GREEN}Congratulations! You won {gold_won} gold!{Colors.RESET}")
                else:
                    print(f"\n{Colors.RED}Sorry, you lose.{Colors.RESET}")
                
                play_again = input(f"\n{Colors.CYAN}Play again? [y/n]: {Colors.RESET}").lower()
                if play_again != 'y':
                    break
            else:
                break
        
        return True
 
    
    def handle_choice_puzzle(self, player):
        """Management of an enigma where the player must choose between several options."""

        puzzle = random.choice(puzzle_choices)

        print(f"\n{Colors.CYAN}{puzzle['description']}{Colors.RESET}")
        print(f"{Colors.GREEN}Choose an option :{Colors.RESET}")

        for key, option in puzzle["options"].items():
            print(f"{Colors.YELLOW}{key}. {option['name']}{Colors.RESET}")

        choice = input(f"\n{Colors.CYAN}Your choice : {Colors.RESET}")

        if choice in puzzle["options"]:
            option = puzzle["options"][choice]
            print(f"\n{Colors.CYAN}{option['message']}{Colors.RESET}")

            effect_type, effect_value = option["effect"]

            if effect_type == "heal":
                player.heal(effect_value)
                print(f"{Colors.GREEN}You recover {effect_value} PV !{Colors.RESET}")
            elif effect_type == "damage":
                player.stats.hp = max(1, player.stats.hp - effect_value)
                print(f"{Colors.RED}You suffer {effect_value} damage !{Colors.RESET}")
            elif effect_type == "attack_boost":
                player.stats.attack += effect_value
                print(f"{Colors.RED}Your attack increases by {effect_value} !{Colors.RESET}")
            elif effect_type == "weapon":
                weapon = generate_random_item(player, item_type="weapon", rarity_boost=1.2)
                player.inventory.append(weapon)
                print(f"{Colors.GREEN}You find a {weapon.name} !{Colors.RESET}")
            elif effect_type == "armor":
                armor = generate_random_item(player, item_type="armor", rarity_boost=1.2)
                player.inventory.append(armor)
                print(f"{Colors.GREEN}You find a {armor.name} !{Colors.RESET}")

            return True

        print(f"\n{Colors.RED}Invalid choice. The puzzle remains sealed.{Colors.RESET}")
        return True
    
    def handle_sequence_puzzle(self, player):
        """Managing a mathematical sequence puzzle."""
        sequence_type = random.choice(["arithmetic", "geometric"])

        if sequence_type == "arithmetic":
            start = random.randint(1, 10)
            difference = random.randint(1, 5)
            sequence = [start + i * difference for i in range(5)]
        else:  # Géométrique
            start = random.randint(1, 5)
            ratio = random.randint(2, 3)
            sequence = [start * (ratio ** i) for i in range(5)]

        print(f"\n{Colors.CYAN}You see a sequence of numbers engraved on the wall:{Colors.RESET}")
        sequence_display = ", ".join(str(num) for num in sequence[:-1])
        print(f"{Colors.YELLOW}{sequence_display}, ?{Colors.RESET}")
        print(f"{Colors.GREEN}Find the missing number to complete the sequence.{Colors.RESET}")

        # Le joueur a 3 tentatives
        for attempt in range(3):
            try:
                answer = int(input(f"\n{Colors.YELLOW}Your response (attempt {attempt+1}/3) : {Colors.RESET}"))

                if answer == sequence[-1]:
                    print(f"\n{Colors.GREEN}Correct answer! A secret compartment opens.{Colors.RESET}")

                    # Récompense aléatoire
                    reward_type = random.choice(["or", "objet", "stat"])
                    if reward_type == "or":
                        gold_amount = random.randint(50, 100) * player.dungeon_level
                        player.gold += gold_amount
                        print(f"{Colors.YELLOW}You find {gold_amount} gold !{Colors.RESET}")
                    elif reward_type == "objet":
                        item = generate_random_item(player=player, rarity_boost=1.2)
                        player.inventory.append(item)
                        print(f"{Colors.GREEN}You find a {item.name} !{Colors.RESET}")
                    elif reward_type == "stat":
                        stat_type = random.choice(["attack", "defense", "hp", "luck", "mana", "stamina"])
                        if stat_type == "attack":
                            player.stats.attack += 1
                            print(f"{Colors.RED}Your attack increases by 1 !{Colors.RESET}")
                        elif stat_type == "defense":
                            player.stats.defense += 1
                            print(f"{Colors.BLUE}Your defense increases by 1 !{Colors.RESET}")
                        elif stat_type == "hp":
                            player.stats.max_hp += 5
                            player.stats.hp += 5
                            print(f"{Colors.GREEN}Your max HP increases by 5 !{Colors.RESET}")
                        elif stat_type == "luck":
                            player.stats.luck += 1
                            print(f"{Colors.CYAN}Your luck increases by 1 !{Colors.RESET}")
                        elif stat_type == "mana":
                            player.stats.mana += 5
                            print(f"{Colors.BRIGHT_CYAN}Your mana increases by 5 !{Colors.RESET}")
                        elif stat_type == "stamina":
                            player.stats.stamina += 5

                    return True
                else:
                    print(f"{Colors.RED}Wrong answer! You're left with {2 - attempt} attempt.{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in number puzzle guess input: {e}")
                print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")
                attempt -= 1  # Ne pas compter une entrée invalide comme une tentative

        print(f"\n{Colors.RED}You have failed to solve the riddle. The mechanism triggers a trap !{Colors.RESET}")
        damage = random.randint(5, 10) * player.dungeon_level
        player.stats.hp = max(1, player.stats.hp - damage)  # Le joueur ne peut pas mourir mais reste à 1 PV min
        print(f"{Colors.RED}You suffer {damage} damage !{Colors.RESET}")

        return True

    def handle_combat(self, player:Player, is_boss_room=False):
        """Gère un combat, normal ou contre un boss, de manière optimisée avec timing-based mechanic et UI améliorée."""
        player.combat_encounters += 1
        import math

        def display_combat_status():
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
            hp_bar = create_bar(player.stats.hp, player.stats.max_hp, color=Colors.RED)
            print(f"\r{Colors.YELLOW}║ {Colors.RED}{hp_text.ljust(box_len)}{Colors.RESET}")
            print(f"\r{Colors.YELLOW}║ {hp_bar.ljust(box_len)}{Colors.RESET}")

            # Stamina
            stamina_text = f"Stamina: {player.stats.stamina}/{player.stats.max_stamina}"
            stamina_bar = create_bar(player.stats.stamina, player.stats.max_stamina, color=Colors.YELLOW)
            print(f"\r{Colors.YELLOW}║ {Colors.YELLOW}{stamina_text.ljust(box_len)}{Colors.RESET}")
            print(f"\r{Colors.YELLOW}║ {stamina_bar.ljust(box_len)}{Colors.RESET}")

            # Mana
            mana_text = f"Mana: {player.stats.mana}/{player.stats.max_mana}"
            mana_bar = create_bar(player.stats.mana, player.stats.max_mana, color=Colors.BRIGHT_BLUE)
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
            enemy_hp_bar = create_bar(enemy.stats.hp, enemy.stats.max_hp, color=Colors.RED)
            print(f"\r{Colors.YELLOW}║ {Colors.RED}{enemy_hp_text.ljust(box_len)}{Colors.RESET}")
            print(f"\r{Colors.YELLOW}║ {enemy_hp_bar.ljust(box_len)}{Colors.RESET}")

            logger.info(f"{enemy.name}: {enemy.stats.hp}/{enemy.stats.max_hp} hp")

            # Bottom border
            print(f"{Colors.YELLOW}╚{'═' * (box_len + 1)}╝{Colors.RESET}")

        if not self.enemies:
            print(f"{Colors.GREEN}The room is empty.{Colors.RESET}")
            return True

        enemy = self.enemies[0]
        input(f'\n{Colors.BOLD}{Colors.RED}Press enter to begin the combat{Colors.RESET}')
        time.sleep(0.3)
        clear_screen()

        if is_boss_room:
            logger.info(f"Boss Enconter: {enemy.name}")
            print(f"\n{Colors.RED}{Colors.BOLD}╔══════════════════════════════════════════╗")
            print(f"║              BOSS ENCOUNTER              ║")
            print(f"╚══════════════════════════════════════════╝{Colors.RESET}")
            typewriter_effect(f"\n{Colors.RED}{Colors.BOLD}The {enemy.name} emerges from the shadows!{Colors.RESET}", 0.03)
            time.sleep(1)
        else:
            logger.info(f"Enemy enconter: {enemy.name}")
            print(f"\n{Colors.RED}A {enemy.name} appears!{Colors.RESET}")
            time.sleep(0.5)

        while enemy.is_alive() and player.is_alive():
            display_combat_status()

            # Player turn
            print(f"\n{Colors.CYAN}Your turn :{Colors.RESET}")
            print(f"{Colors.YELLOW}1. Attack{Colors.RESET}")
            if player.skills:
                print(f"{Colors.MAGENTA}2. Use Skill{Colors.RESET}")
            print(f"{Colors.GREEN}3. Use Item{Colors.RESET}")
            if not is_boss_room:
                print(f"{Colors.BRIGHT_YELLOW}4. Try to Run{Colors.RESET}")

            choice = input(f"\n{Colors.CYAN}What will you do? {Colors.RESET}")

            if choice == "1":  # Normal attack without timing mechanic (simpler)
                base_damage = player.total_domage()

                # Critical hit chance
                critical = random.random() < (0.025 + player.stats.luck * 0.01 + player.stats.critical_chance * 0.02)
                if critical:
                    base_damage *= 2
                    print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}CRITICAL HIT!{Colors.RESET}")

                # Stamina cost
                if player.equipment.main_hand:
                    stamina_cost = 5
                elif player.equipment.off_hand:
                    stamina_cost = 10
                else:
                    stamina_cost = 2

                if player.stats.stamina >= stamina_cost:
                    player.use_stamina(stamina_cost)
                else:
                    print(f"{Colors.RED}You're exhausted! Your attack is weaker...{Colors.RESET}")
                    base_damage /= 2

                damage, absorbed_damage = enemy.stats.take_damage(base_damage)
                actual_damage = damage + absorbed_damage
                logger.info(f"Player attack: {'critical hit' if critical else ''} {actual_damage} dmg, {stamina_cost} stm")
                print(f"You deal {Colors.RED}{math.ceil(actual_damage)}{Colors.RESET} damage to {enemy.name}!")

            elif choice == "2" and player.skills:  # Use skill with timing mechanic
                player.use_skill(enemy)

            elif choice == "3":  # Use item
                potions = [item for item in player.inventory if isinstance(item, Potion)]
                if not potions:
                    print(f"{Colors.RED}You don't have any usable items in combat!{Colors.RESET}")
                    continue
                
                print(f"\n{Colors.GREEN}Your Items:{Colors.RESET}")
                for i, item in enumerate(potions, 1):
                    print(f"{Colors.YELLOW}{i}. {item}{Colors.RESET}")

                try:
                    item_choice = int(input(f"\n{Colors.CYAN}Choose an item to use (0 to cancel): {Colors.RESET}"))
                    if 1 <= item_choice <= len(potions):
                        potions[item_choice - 1].use(player)
                    else:
                        print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Please enter a number.{Colors.RESET}")
                    continue

            elif choice == "4" and not is_boss_room:  # Try to run
                if random.random() < (0.3 + player.stats.luck * 0.03):
                    print(f"{Colors.GREEN}You successfully escape!{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.RED}You failed to escape!{Colors.RESET}")

            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")
                continue

            # Check if enemy defeated
            if not enemy.is_alive():
                player.kills += 1
                player.souls += 1
                player.gold += enemy.gold_reward
                print(f"\n{Colors.GREEN}You defeated the {enemy.name}!{Colors.RESET}\n")
                player.gain_xp(enemy.xp_reward)
                print(f"{Colors.YELLOW}You gain {enemy.gold_reward} gold!{Colors.RESET}")
                print(f"{Colors.BRIGHT_BLACK}You gain 1 souls!{Colors.RESET}\n")

                # Item drop
                if is_boss_room:
                    dropped_item = generate_random_item(player=player, enemy=enemy, rarity_boost=1.5)

                elif random.random() < (0.2 + player.stats.luck * 0.02):
                    dropped_item = generate_random_item(player=player, enemy=enemy)
                    player.inventory.append(dropped_item)
                    print(f"{Colors.GREEN}The {enemy.name} dropped: {dropped_item.name}!{Colors.RESET}")
                    time.sleep(2)

                self.enemies.remove(enemy)

                # Quest progress
                """
                for quest in player.quests:
                    if quest.objective_type == "kill_enemies" and not quest.completed:
                        if quest.update_progress():
                            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
                """
                player.update_quests("kill_enemies")


                if self.enemies:
                    enemy = self.enemies[0]
                    print(f"\n{Colors.RED}A {enemy.name} appears!{Colors.RESET}")
                    time.sleep(0.5)
                else:
                    return True

            # Enemy turn
            if enemy.is_alive():
                print(f"\n{Colors.RED}{enemy.name} attacks!{Colors.RESET}")
                time.sleep(0.5)
                if random.random() < (player.stats.luck * 0.01 + player.stats.agility * 0.02):
                    print(f"{Colors.GREEN}You dodged the attack!{Colors.RESET}")
                else:
                    enemy.attack_player(player)
                time.sleep(0.5)
        return player.is_alive()

    
    def handle_treasure(self, player:Player):
        """Handles treasure room interactions."""
        player.treasures_found += 1
        if not self.items:
            print(f"{Colors.YELLOW}You've already collected all treasure from this room.{Colors.RESET}")
            return True
        
        print(f"\n{Colors.GREEN}You found a treasure!{Colors.RESET}")

        time.sleep(0.5)
        
        for item in self.items[:]:
            player.inventory.append(item)
            print(f"{Colors.GREEN}You acquired: {item.name}{Colors.RESET}")
            
            # Update quest progress if applicable
            for quest in player.quests:
                if quest.objective_type == "find_items" and not quest.completed:
                    if quest.update_progress():
                        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
        
        # Clear items so they can't be collected again
        self.items.clear()
        
        return True
    
    def handle_shop(self, player:Player, box=False):
        player.shops_visited += 1
        def print_box(title, lines, color_title=Colors.BRIGHT_CYAN, color_border=Colors.BRIGHT_CYAN, color_text=Colors.RESET):
            width = max(len(line) for line in lines + [title]) + 2
            print(f"{color_border}╔{'═' * width}╗{Colors.RESET}")
            print(f"{color_border}╠{'═' * width}╣{Colors.RESET}")
            print(f"{color_border}║ {color_title}{title.center(width - 2)} {color_border}║{Colors.RESET}")
            print(f"{color_border}╠{'═' * width}╣{Colors.RESET}")
            for line in lines:
                print(f"{color_border}║ {color_text}{line.ljust(width - 2)} {color_border}║{Colors.RESET}")
            print(f"{color_border}╚{'═' * width}╝{Colors.RESET}")

        def print_merchant_dialogue_box(name, dialogue):
            name_width = max(len(name) + 4, 10)
            dialogue_width = max(len(dialogue) + 4, 30)
            total_width = name_width + dialogue_width

            # Top border of name box and dialogue box
            print(f"{Colors.BRIGHT_CYAN}╔{'═' * name_width}╗{Colors.RESET}")
            # Name line
            print(f"{Colors.BRIGHT_CYAN}║{Colors.YELLOW} {name.ljust(name_width - 1)}{Colors.BRIGHT_CYAN}║{Colors.RESET}")
            # Separator line between name box and dialogue box
            print(f"{Colors.BRIGHT_CYAN}╠{'═' * name_width}╩{'═' * (dialogue_width - name_width - 1)}╗{Colors.RESET}")
            # Dialogue lines box (top border)
            print(f"{Colors.BRIGHT_CYAN}║{Colors.YELLOW} {dialogue.ljust(dialogue_width - 2)} {Colors.BRIGHT_CYAN}║{Colors.RESET}")
            # Bottom border of dialogue box
            print(f"{Colors.BRIGHT_CYAN}╚{'═' * dialogue_width}╝{Colors.RESET}")

        def print_shop_box(gold_line, items_lines):
            width = max(len(gold_line), max((len(line) for line in items_lines), default=0)) + 2
            # Top border
            print(f"{Colors.BRIGHT_YELLOW}╔{'═' * width}╗{Colors.RESET}")
            # Gold line
            print(f"{Colors.BRIGHT_YELLOW}║ {Colors.GREEN}{gold_line.ljust(width - 2)} {Colors.BRIGHT_YELLOW}║{Colors.RESET}")
            # Separator
            print(f"{Colors.BRIGHT_YELLOW}╠{'═' * width}╣{Colors.RESET}")
            # Items lines
            for line in items_lines:
                print(f"{Colors.BRIGHT_YELLOW}║ {Colors.YELLOW}{line.ljust(width - 2)} {Colors.BRIGHT_YELLOW}║{Colors.RESET}")
            # Bottom border
            print(f"{Colors.BRIGHT_YELLOW}╚{'═' * width}╝{Colors.RESET}")

        shopkeeper_names = ["Grimble", "Zara", "Old Finn", "Mysteria", "Drogon"]
        shopkeeper = random.choice(shopkeeper_names)

        clear_screen()

        # Merchant dialogue box with two horizontally adjacent boxes
        merchant_name = f"{shopkeeper}"
        merchant_dialogue = "Welcome to my shop, traveler! What can I interest you in today?"
        print_merchant_dialogue_box(merchant_name, merchant_dialogue)

        # Generate shop inventory
        shop_inventory = []
        for _ in range(player.difficulty.get_shop_item_num()):
            shop_inventory.append(generate_random_item(player=player))

        shop_inventory.sort(key=lambda item: item.value, reverse=True)

        shopping = True
        while shopping:
            # Player gold and shop items box with colors and horizontal separator
            gold_line = f"{Colors.YELLOW}Your gold: {player.gold}{Colors.RESET}"
            items_lines = [f"{Colors.YELLOW}{i}. {item} - {Colors.BRIGHT_YELLOW}{item.value} gold{Colors.RESET}" for i, item in enumerate(shop_inventory, 1)]

            if box:
                print_shop_box(gold_line, items_lines)
            else:
                print(gold_line)
                for line in items_lines:
                    print(line)

            print(f"\n{Colors.BRIGHT_CYAN}What would you like to do?{Colors.RESET}")
            print(f"{Colors.YELLOW}1-{len(shop_inventory)}. Buy item{Colors.RESET}")
            print(f"{Colors.GREEN}S. Sell items{Colors.RESET}")
            print(f"{Colors.RED}L. Leave shop{Colors.RESET}")

            choice = input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}").upper()

            if choice == "S":
                self.sell_items(player, shopkeeper)
            elif choice == "L":
                print(f"\n{Colors.BRIGHT_CYAN}{shopkeeper}: Come back soon!{Colors.RESET}")
                shopping = False
            else:
                try:
                    item_index = int(choice) - 1
                    if 0 <= item_index < len(shop_inventory):
                        item = shop_inventory[item_index]
                        if player.gold >= item.value:
                            player.gold -= item.value
                            player.gold_spent += item.value
                            player.inventory.append(item)
                            shop_inventory.remove(item)
                            print(f"\n{Colors.GREEN}You bought {item.name} for {item.value} gold.{Colors.RESET}")
                        else:
                            print(f"\n{Colors.RED}You don't have enough gold!{Colors.RESET}")
                    else:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError as e:
                    logger.warning(f"ValueError in shop item choice input: {e}")
                    print(f"\n{Colors.RED}Please enter a valid option.{Colors.RESET}")

        return True

    def sell_items(self, player, shopkeeper):
        global debug
        
        if debug >= 1:
            print(f"DEBUG: Inventory before selling -> {player.inventory}")
        
        if not player.inventory:
            print(f"\n{Colors.RED}You don't have any items to sell!{Colors.RESET}")
            return
        
        print(f"\n{Colors.BRIGHT_CYAN}{shopkeeper}: What would you like to sell?{Colors.RESET}")
        
        for i, item in enumerate(player.inventory, 1):
            sell_value = int(item.value * 0.5)  
            print(f"{Colors.YELLOW}{i}. {item} - Sell for {Colors.BRIGHT_YELLOW}{sell_value} gold{Colors.RESET}")
        
        print(f"{Colors.RED}0. Cancel{Colors.RESET}")
        
        try:
            choice = int(input(f"\n{Colors.CYAN}Choose an item to sell (0 to cancel): {Colors.RESET}"))
            
            if choice == 0:
                return
            elif 1 <= choice <= len(player.inventory):
                item = player.inventory[choice - 1]
                sell_value = int(item.value * 0.5)
                
                if debug >= 1:
                    print(f"DEBUG: Selling {item.name} for {sell_value} gold")
                
                player.gold += sell_value
                player.inventory.remove(item)
                print(f"\n{Colors.GREEN}You sold {item.name} for {sell_value} gold.{Colors.RESET}\n")
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        
        except ValueError as e:
            logger.warning(f"ValueError in sell item choice input: {e}")
            print(f"\n{Colors.RED}Please enter a number.{Colors.RESET}")


    def handle_rest(self, player:Player):
        """Gère le repos du joueur, permettant de récupérer des PV, de la mana et de l'endurance."""
        player.rest_rooms_visited += 1
        print(f"\n{Colors.CYAN}You find a safe place to rest.{Colors.RESET}")
        
        options = [
            "Rest and recover HP, stamina and some mana",
            "Meditate and recover a small amount of HP while training",
            "Examine your inventory"
            "Continue"
        ]
        
        for i, option in enumerate(options, 1):
            print(f"{Colors.YELLOW}{i}. {option}{Colors.RESET}")
        
        choice = input(f"\n{Colors.CYAN}What would you like to do? {Colors.RESET}")
        if choice not in ["1", "2", "3", "4"]:
            print(f"\n{Colors.RED}Invalid choice. It's your last change.{Colors.RESET}")
            choice = input(f"{Colors.YELLOW}your choice: {Colors.RESET}")
        
        if choice == "1":
            # Rest and recover 30-50% of max HP
            recovery_percent_hp = random.uniform(0.3, 0.5)
            recovery_amount_hp = int(player.stats.max_hp * recovery_percent_hp)
            old_hp = player.stats.hp
            player.heal(recovery_amount_hp)

            # add stamina with player.rest_stamina(amount), and mana with regen_mana(amount):
            recovery_percent_stamina = random.uniform(0.2, 0.6)
            recovery_amount_stamina = int(player.stats.max_stamina * recovery_percent_stamina)
            old_stamina = player.stats.stamina
            player.rest_stamina(recovery_amount_stamina)

            recovery_percent_mana = random.uniform(0.2, 0.4)
            recovery_amount_mana = int(player.stats.max_mana * recovery_percent_mana)
            old_mana = player.stats.mana
            player.regen_mana(recovery_amount_mana)

            print(f"\n{Colors.GREEN}You rest peacefully and recover {player.stats.hp - old_hp} HP.{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}You also recover {player.stats.stamina - old_stamina} Stamina.{Colors.RESET}")
            print(f"{Colors.BRIGHT_CYAN}And {player.stats.mana - old_mana} Mana.{Colors.RESET}")
            
            # Small chance of random event during rest
            if random.random() < 0.2:
                self.random_rest_event(player)
                
        elif choice == "2":
            # Meditate - recover less HP but get small stat boost
            recovery_percent_hp = random.uniform(0.3, 0.5)
            recovery_amount_hp = int(player.stats.max_hp * recovery_percent_hp)
            old_hp = player.stats.hp
            player.heal(recovery_amount_hp)

            # Recover some Stamina
            recovery_percent_stamina = random.uniform(0.2, 0.6)
            recovery_amount_stamina = int(player.stats.max_stamina * recovery_percent_stamina)
            old_stamina = player.stats.stamina
            player.rest_stamina(recovery_amount_stamina)

            # Recover some Mana
            recovery_percent_mana = random.uniform(0.2, 0.4)
            recovery_amount_mana = int(player.stats.max_mana * recovery_percent_mana)
            old_mana = player.stats.mana
            player.regen_mana(recovery_amount_mana)
            
            print(f"\n{Colors.GREEN}You meditate and recover {player.stats.hp - old_hp} HP.{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}You also recover {player.stats.stamina - old_stamina} Stamina.{Colors.RESET}")
            print(f"{Colors.BRIGHT_CYAN}And {player.stats.mana - old_mana} Mana.{Colors.RESET}")
            
            # Small random stat boost
            possible_boosts = {
                "attack": (Colors.RED, "Your combat training improved your Attack by 1!"),
                "defense": (Colors.BLUE, "Your defensive techniques improved your Defense by 1!"),
                "luck": (Colors.CYAN, "Your intuition improved your Luck by 1!"),
                "agility": (Colors.GREEN, "Your footwork improved your Agility by 1!"),
                "max_hp": (Colors.BRIGHT_RED, "Your endurance increased, gaining +5 Max HP!"),
            }

            stat_boost = random.choice(list(possible_boosts.keys()))
            color, message = possible_boosts[stat_boost]

            if stat_boost == "max_hp":
                player.stats.modify_stat(stat_boost, 5, permanent=True)
            else:
                player.stats.modify_stat(stat_boost, 1, permanent=True)
            
            print(f"{color}{message}{Colors.RESET}")


        elif choice == "3":
            player.manage_inventory(player)
            
        else:
            print(f"{Colors.RED}Your choice:{Colors.RESET}", choice)
            print(f"{Colors.BLUE}You decided to keep going.{Colors.RESET}")
        
        return True
    
    def random_rest_event(self, player):
        
        rest_event = random.choice(rest_events)
        print(f"\n{Colors.YELLOW}While resting: {rest_event['description']}{Colors.RESET}")
        
        if rest_event["effect"] == "luck":
            player.stats.luck += rest_event["value"]
            print(f"{Colors.CYAN}Luck increased by {rest_event['value']}!{Colors.RESET}")
        elif rest_event["effect"] == "attack":
            player.stats.attack += rest_event["value"]
            print(f"{Colors.RED}Attack increased by {rest_event['value']}!{Colors.RESET}")
        elif rest_event["effect"] == "defense":
            player.stats.defense += rest_event["value"]
            print(f"{Colors.BLUE}Defense increased by {rest_event['value']}!{Colors.RESET}")
        elif rest_event["effect"] == "item":
            item = generate_random_item(player=player)
            player.inventory.append(item)
            print(f"{Colors.GREEN}You received: {item.name}!{Colors.RESET}")
        elif rest_event["effect"] == "gold":
            player.gold = max(0, player.gold + rest_event["value"])
            if rest_event["value"] < 0:
                print(f"{Colors.RED}You lost {abs(rest_event['value'])} gold!{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}You gained {rest_event['value']} gold!{Colors.RESET}")

def generate_shop_inventory(level):
    logger.info(f"Generating shop inventory for level {level}")
    shop_items = [
        Weapon("Short Sword", "A basic sword for beginners.", 30, 4),
        Weapon("Iron Mace", "A heavy but strong weapon.", 50, 6),
        Armor("Leather Boots", "Light armor that improves movement.", 20, 2),
        Armor("Steel Breastplate", "Good protection for adventurers.", 70, 6),
        Potion("Healing Potion", "Restores 30 HP.", 25, "heal", 30),
        Potion("Strength Elixir", "Increases attack power.", 40, "attack_boost", 5)
    ]
    logger.debug(f"Shop items generated: {[item.name for item in shop_items]}")
    logger.info(f"Returning {min(len(shop_items), 5)} items for sale")
    return random.sample(shop_items, min(len(shop_items), 5))  # Randomly pick 5 items for sale


def generate_random_room(player, room_type=None, is_boss_room=False):
    """Generate a random room for the given dungeon level"""
    global debug

    level = player.dungeon_level
    if room_type is None:
        weights = [0.5, 0.2, 0.1, 0.15, 0.05]
        room_type = random.choices(["combat", "treasure", "shop", "rest", "puzzle"], weights=weights)[0]
    
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Generating random room of type '{room_type}' for level {level}{Colors.RESET}")
    logger.info(f"Generating random room of type '{room_type}' for level {level}")
    
    if is_boss_room:
        room_type = "boss"
        logger.info("Generating boss room")
    
    description = random.choice(room_descriptions[room_type])
    
    enemies = []
    items = []
    trap = None
    
    # Generate enemies for combat and boss rooms
    if room_type in ["combat", "boss"]:
        num_enemies = 1 if room_type == "boss" else random.randint(1, 2 + level // 3)
        for _ in range(num_enemies):
            enemies.append(generate_enemy(level, is_boss_room, player))
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Enemies generated: {enemies}{Colors.RESET}")
        logger.debug(f"Generated {len(enemies)} enemies for room")
    # Generate items for treasure rooms
    if room_type == "treasure":
        num_items = random.randint(1, 2)
        for _ in range(num_items):
            items.append(generate_random_item(player=player))
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Items generated: {items}{Colors.RESET}")
    logger.debug(f"Generated item: {items}")
    
    # Generate trap (30% chance) for all rooms except rest, shop, and inter_level
    if room_type not in ("rest", "shop", "inter_level") and random.random() < 0.3:
        trap_types = [
            {"type": "damage", "value": 5 + level * 2, "description": "A poisoned dart shoots from the wall!"},
            {"type": "damage", "value": 3 + level * 3, "description": "The floor opens up to reveal spikes!"},
            {"type": "stat_reduction", "stat": "attack", "value": 2, "description": "A strange gas makes your muscles weaken!"},
            {"type": "stat_reduction", "stat": "defense", "value": 2, "description": "A curse makes your skin more vulnerable!"}
        ]
        trap = random.choice(trap_types)
        trap["triggered"] = False
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Trap generated: {trap}{Colors.RESET}")
    logger.info(f"Trap generated: {trap}")
    
    return Room(room_type, description, enemies, items, trap)

def generate_dungeon(player:Player):
    """Generates a dungeon with rooms based on the level and difficulty."""
    global debug
    dungeon_level = player.dungeon_level
    difficulty = player.difficulty
    rooms = []
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Generating dungeon level {dungeon_level} with difficulty {difficulty}{Colors.RESET}")
    logger.info(f"Starting dungeon generation for level {dungeon_level} with difficulty {difficulty}")
    
    # Définition du nombre de salles selon la difficulté
    """
    if difficulty == "normal":
        num_rooms = random.randint(5, 8)
    elif difficulty == "soul_enjoyer":
        num_rooms = random.randint(5, 8)
    elif difficulty == "realistic":
        num_rooms = random.randint(10, 20)
    else:
        print(f"{Colors.RED}Invalid difficulty level.{Colors.RESET}")
        print(difficulty)
        num_rooms = random.randint(5, 8)
        input()
    """
    num_rooms = player.difficulty.get_room_count()
    logger.debug(f"Number of rooms to generate: {num_rooms}")
    
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Number of rooms: {num_rooms}{Colors.RESET}")
    
    # Starting room
    if dungeon_level == 1:
        logger.debug(f"Generating Starting room")
        rooms.append(Room("start", f"You noticed the entrance to the dungeon.\nYou finaly decided to open the door and step in.\nTorches flicker on the damp walls, and the air is heavy with anticipation.", [], [], None))
        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Starting room added{Colors.RESET}")
    else:
        # Inter-level room:
        logger.debug(f"Generating Inter-level room")
        rooms.append(Room("inter_level", f"You find a small room with a few torches and a table.\nIt seems like a resting place for adventurers.", [], [], None))
        if debug >= 1:
            print(f"{Colors.YELLOW}DEBUG: Inter-level room added{Colors.RESET}")

    for i in range(1, num_rooms):
        rooms.append(generate_random_room(player=player))
        logger.debug(f"Room generated: {rooms[i]}")
    
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Generated {len(rooms)} rooms :{Colors.RESET}")
        for room in rooms:
            print(f"{Colors.YELLOW}DEBUG: Room type: {room.room_type}, Description: {room.description}, Enemies: {room.enemies}, Items: {room.items}, Trap: {room.trap}{Colors.RESET}")

    rooms.append(generate_random_room(player=player, is_boss_room=True))
    
    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Boss room added{Colors.RESET}")

    if debug >= 1:
        print(f"{Colors.YELLOW}DEBUG: Dungeon generation complete:{Colors.RESET}")
        print(f"{Colors.YELLOW}DEBUG: Rooms: {rooms}{Colors.RESET}")

    return rooms

"""
    def choose_next_room(self, player):
        print(f"\n{Colors.YELLOW}Where would you like to go next?{Colors.RESET}")
        
        # Get available rooms (excluding current)
        available_rooms = [room for room in self.dungeon if room != self.current_room]
        
        # If all rooms have been visited, include boss room no matter what
        boss_room = next((room for room in self.dungeon if room.room_type == "boss"), None)
        all_visited = all(room.visited for room in self.dungeon if room != boss_room)
        
        # Only show 3 random options, always include boss room if all others visited
        if len(available_rooms) > 3 and not all_visited:
            options = random.sample(available_rooms, 3)
            if boss_room and boss_room.visited is False and boss_room not in options and all_visited:
                options[0] = boss_room
        else:
            options = available_rooms
        
        for i, room in enumerate(options, 1):
            room_name = f"the Boss Chamber" if room.room_type == "boss" else f"a {room.room_type.capitalize()} Room"
            if room.visited:
                room_name += " (Revisit)"
            print(f"{Colors.CYAN}{i}. Go to {room_name}{Colors.RESET}")
        
        print(f"{Colors.CYAN}{len(options) + 1}. Check Inventory/Equipment{Colors.RESET}")
        print(f"{Colors.CYAN}{len(options) + 2}. Check Quests{Colors.RESET}")
        print(f"{Colors.CYAN}{len(options) + 3}. Save Game{Colors.RESET}")
        print(f"{Colors.CYAN}{len(options) + 4}. Quit Game{Colors.RESET}")
        
        while True:
            try:
                choice = int(input(f"\n{Colors.YELLOW}Enter your choice: {Colors.RESET}"))
                
                if 1 <= choice <= len(options):
                    self.current_room = options[choice - 1]
                    break
                elif choice == len(options) + 1:
                    self.manage_inventory()
                elif choice == len(options) + 2:
                    self.view_quests(player)
                elif choice == len(options) + 3:
                    save_name = input(f"{Colors.YELLOW}Enter save name: {Colors.RESET}")
                    player.save_player(save_name)
                elif choice == len(options) + 4:
                    self.quit_game()
                    break
                else:
                    print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and {len(options) + 4}.{Colors.RESET}")
            
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")

    def manage_inventory(self):
        clear_screen()
        print(f"\n{Colors.YELLOW}{Colors.BOLD}╔═══════════════════ INVENTORY ═══════════════════╗{Colors.RESET}")
        
        if not self.player.inventory:
            print(f"{Colors.RED}Your inventory is empty.{Colors.RESET}")
        else:
            for i, item in enumerate(self.player.inventory, 1):
                equipped = ""
                if isinstance(item, Weapon) and item == self.player.equipment.weapon:
                    equipped = f" {Colors.GREEN}[EQUIPPED]{Colors.RESET}"
                elif isinstance(item, Armor) and item == self.player.equipment.armor:
                    equipped = f" {Colors.GREEN}[EQUIPPED]{Colors.RESET}"
                
                print(f"{Colors.CYAN}{i}. {item}{equipped}{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Options:{Colors.RESET}")
        print(f"{Colors.CYAN}1. Use/Equip an item{Colors.RESET}")
        print(f"{Colors.CYAN}2. Examine an item{Colors.RESET}")
        print(f"{Colors.CYAN}3. Drop an item{Colors.RESET}")
        print(f"{Colors.CYAN}4. Return to exploration{Colors.RESET}")
        
        while True:
            choice = input(f"\n{Colors.YELLOW}What would you like to do? {Colors.RESET}")
            
            if choice == "1":  # Use/Equip
                if not self.player.inventory:
                    print(f"{Colors.RED}You don't have any items to use or equip!{Colors.RESET}")
                    continue
                
                try:
                    item_choice = int(input(f"\n{Colors.CYAN}Enter the number of the item you want to use/equip (0 to cancel): {Colors.RESET}"))
                    if 1 <= item_choice <= len(self.player.inventory):
                        item = self.player.inventory[item_choice-1]
                        
                        if isinstance(item, Weapon):
                            self.player.equipment.weapon = item
                            print(f"\n{Colors.GREEN}You equipped {item.name}!{Colors.RESET}")
                        elif isinstance(item, Armor):
                            self.player.equipment.armor = item
                            print(f"\n{Colors.GREEN}You equipped {item.name}!{Colors.RESET}")
                        elif isinstance(item, Potion):
                            item.use(self.player)
                        else:
                            print(f"\n{Colors.YELLOW}You can't use this item right now.{Colors.RESET}")
                    elif item_choice != 0:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError:
                    print(f"\n{Colors.RED}Please enter a number.{Colors.RESET}")
            
            elif choice == "2":  # Examine
                if not self.player.inventory:
                    print(f"{Colors.RED}You don't have any items to examine!{Colors.RESET}")
                    continue
                
                try:
                    item_choice = int(input(f"\n{Colors.CYAN}Enter the number of the item you want to examine (0 to cancel): {Colors.RESET}"))
                    if 1 <= item_choice <= len(self.player.inventory):
                        item = self.player.inventory[item_choice-1]
                        print(f"\n{Colors.CYAN}Name: {item.name}{Colors.RESET}")
                        print(f"{Colors.CYAN}Description: {item.description}{Colors.RESET}")
                        
                        if isinstance(item, Weapon):
                            print(f"{Colors.RED}Damage: +{item.damage}{Colors.RESET}")
                        elif isinstance(item, Armor):
                            print(f"{Colors.BLUE}Defense: +{item.defense}{Colors.RESET}")
                        elif isinstance(item, Potion):
                            effect_desc = ""
                            if item.effect_type == "heal":
                                effect_desc = f"Heals {item.effect_value} HP"
                            elif item.effect_type == "attack_boost":
                                effect_desc = f"Increases Attack by {item.effect_value}"
                            elif item.effect_type == "defense_boost":
                                effect_desc = f"Increases Defense by {item.effect_value}"
                            print(f"{Colors.GREEN}Effect: {effect_desc}{Colors.RESET}")
                        
                        print(f"{Colors.YELLOW}Value: {item.value} gold{Colors.RESET}")
                    elif item_choice != 0:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError:
                    print(f"\n{Colors.RED}Please enter a number.{Colors.RESET}")
            
            elif choice == "3":  # Drop
                if not self.player.inventory:
                    print(f"{Colors.RED}You don't have any items to drop!{Colors.RESET}")
                    continue
                
                try:
                    item_choice = int(input(f"\n{Colors.CYAN}Enter the number of the item you want to drop (0 to cancel): {Colors.RESET}"))
                    if 1 <= item_choice <= len(self.player.inventory):
                        item = self.player.inventory[item_choice-1]
                        
                        # Check if item is equipped
                        if item == self.player.equipment.weapon:
                            confirm = input(f"\n{Colors.RED}This item is equipped as your weapon. Are you sure you want to drop it? [y/n]: {Colors.RESET}").lower()
                            if confirm != 'y':
                                continue
                            self.player.equipment.weapon = None
                        elif item == self.player.equipment.armor:
                            confirm = input(f"\n{Colors.RED}This item is equipped as your armor. Are you sure you want to drop it? [y/n]: {Colors.RESET}").lower()
                            if confirm != 'y':
                                continue
                            self.player.equipment.armor = None
                        
                        self.player.inventory.remove(item)
                        print(f"\n{Colors.YELLOW}You dropped {item.name}.{Colors.RESET}")
                    elif item_choice != 0:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError:
                    print(f"\n{Colors.RED}Please enter a number.{Colors.RESET}")
            
            elif choice == "4":  # Back
                return
    
    def handle_shop(self, player):
        clear_screen()
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}╔══════════════════════════════════╗")
        print(f"║       WANDERING MERCHANT       ║")
        print(f"╚══════════════════════════════════╝{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}A mysterious merchant has set up shop in this room.{Colors.RESET}")
        print(f"{Colors.YELLOW}You have {player.gold} gold.{Colors.RESET}")
        
        # Generate items for sale if not already generated
        if not hasattr(self, 'shop_items'):
            self.shop_items = []
            for _ in range(4):
                self.shop_items.append(generate_random_item(player.dungeon_level))
            # Always offer at least one potion
            self.shop_items.append(generate_random_item(player.dungeon_level, "potion"))
        
        while True:
            print(f"\n{Colors.BRIGHT_YELLOW}Items for sale:{Colors.RESET}")
            for i, item in enumerate(self.shop_items, 1):
                price = item.value
                print(f"{Colors.YELLOW}{i}. {item} - {price} gold{Colors.RESET}")
            
            print(f"\n{Colors.CYAN}What would you like to do?{Colors.RESET}")
            print(f"1. {Colors.GREEN}Buy an item{Colors.RESET}")
            print(f"2. {Colors.RED}Sell an item{Colors.RESET}")
            print(f"3. {Colors.CYAN}Leave shop{Colors.RESET}")
            
            choice = input(f"\n{Colors.YELLOW}Enter your choice: {Colors.RESET}")
            
            if choice == "1":  # Buy
                try:
                    item_choice = int(input(f"\n{Colors.CYAN}Enter the number of the item you wish to buy (0 to cancel): {Colors.RESET}"))
                    if item_choice == 0:
                        continue
                    
                    if 1 <= item_choice <= len(self.shop_items):
                        item = self.shop_items[item_choice - 1]
                        price = item.value
                        
                        if player.gold >= price:
                            player.gold -= price
                            player.inventory.append(item)
                            self.shop_items.pop(item_choice - 1)
                            print(f"\n{Colors.GREEN}You bought the {item.name} for {price} gold.{Colors.RESET}")
                            
                            # Replace sold item with a new one
                            if random.random() < 0.5:  # 50% chance to restock
                                new_item = generate_random_item(player.dungeon_level)
                                self.shop_items.append(new_item)
                                print(f"{Colors.YELLOW}The merchant restocks with a {new_item.name}.{Colors.RESET}")
                        else:
                            print(f"\n{Colors.RED}You don't have enough gold!{Colors.RESET}")
                    else:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError:
                    print(f"\n{Colors.RED}Please enter a number.{Colors.RESET}")
            
            elif choice == "2":  # Sell
                if not player.inventory:
                    print(f"\n{Colors.RED}You don't have any items to sell!{Colors.RESET}")
                    continue
                
                print(f"\n{Colors.GREEN}Your Items:{Colors.RESET}")
                for i, item in enumerate(player.inventory, 1):
                    sell_price = item.value // 2  # Sell for half the buy price
                    print(f"{Colors.YELLOW}{i}. {item} - Sell for {sell_price} gold{Colors.RESET}")
                
                try:
                    item_choice = int(input(f"\n{Colors.CYAN}Enter the number of the item you wish to sell (0 to cancel): {Colors.RESET}"))
                    if item_choice == 0:
                        continue
                    
                    if 1 <= item_choice <= len(player.inventory):
                        item = player.inventory[item_choice - 1]
                        sell_price = item.value // 2
                        
                        # Confirm sale
                        confirm = input(f"\n{Colors.YELLOW}Sell {item.name} for {sell_price} gold? (y/n): {Colors.RESET}").lower()
                        if confirm == 'y':
                            player.gold += sell_price
                            player.inventory.remove(item)
                            print(f"\n{Colors.GREEN}You sold the {item.name} for {sell_price} gold.{Colors.RESET}")
                        else:
                            print(f"\n{Colors.YELLOW}Sale canceled.{Colors.RESET}")
                    else:
                        print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                except ValueError:
                    print(f"\n{Colors.RED}Please enter a number.{Colors.RESET}")
            
            elif choice == "3":  # Leave
                print(f"\n{Colors.CYAN}You leave the shop. The merchant nods farewell.{Colors.RESET}")
                return True
            
            else:
                print(f"\n{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")
    
    def handle_treasure(self, player):
        if not self.items:
            print(f"{Colors.YELLOW}You've already collected all the treasure in this room.{Colors.RESET}")
            return True
        
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}You found a treasure!{Colors.RESET}")
        
        # Chance for trapped chest based on dungeon level
        if random.random() < 0.1 * player.dungeon_level / 10:
            print(f"\n{Colors.RED}The treasure chest seems trapped...{Colors.RESET}")
            print(f"1. {Colors.YELLOW}Attempt to disarm the trap (Luck check){Colors.RESET}")
            print(f"2. {Colors.GREEN}Open it anyway{Colors.RESET}")
            print(f"3. {Colors.CYAN}Leave it alone{Colors.RESET}")
            
            choice = input(f"\n{Colors.YELLOW}What will you do? {Colors.RESET}")
            
            if choice == "1":  # Disarm
                if random.random() < (0.4 + player.stats.luck * 0.04):
                    print(f"\n{Colors.GREEN}You successfully disarm the trap!{Colors.RESET}")
                else:
                    trap_damage = random.randint(5, 15) * player.dungeon_level
                    player.stats.hp = max(0, player.stats.hp - trap_damage)
                    print(f"\n{Colors.RED}You trigger the trap! You take {trap_damage} damage!{Colors.RESET}")
                    
                    if not player.is_alive():
                        return False
            
            elif choice == "3":  # Leave
                print(f"\n{Colors.CYAN}You decide to leave the chest untouched.{Colors.RESET}")
                return True
            
            # If choice is 2 or disarm was attempted, continue to opening the chest
        
        # Gold reward
        gold_reward = random.randint(10, 30) * player.dungeon_level
        player.gold += gold_reward
        print(f"{Colors.YELLOW}You found {gold_reward} gold!{Colors.RESET}")
        
        # Items
        for item in self.items:
            print(f"{Colors.GREEN}You found: {item.name}!{Colors.RESET}")
            player.inventory.append(item)
        
        # Clear items from the room
        self.items = []
        
        return True
    
    def handle_puzzle2(self, player):
        puzzles = [
            {
                "description": "A magical riddle is inscribed on the wall.",
                "question": "I'm light as a feather, but even the strongest person can't hold me for more than a minute. What am I?",
                "options": ["A feather", "Breath", "Time", "Thought"],
                "answer": "Breath",
                "reward_gold": 30,
                "reward_xp": 40
            },
        ]
"""

def debug_menu(player, dungeon):
    """
    Opens a debug menu to modify player stats, give items, change dungeon level, or test game mechanics.
    
    Parameters:
        player (Player): The current player instance.
        dungeon (Dungeon): The current dungeon instance.
    
    Options:
        1. Give Item
        2. Modify Player Stats
        3. Set Dungeon Level
        4. Teleport to Room
        5. Spawn Enemies in Current Room
        6. Instantly Complete a Quest
        7. Heal Player
        8. Save Game
        9. Load Game
        0. Exit Debug Menu
    """

    while True:
        print(f"\n{Colors.MAGENTA}=== DEBUG MENU ==={Colors.RESET}")
        print(f"{Colors.YELLOW}1.{Colors.RESET} Give Item")
        print(f"{Colors.YELLOW}2.{Colors.RESET} Modify Player Stats")
        print(f"{Colors.YELLOW}3.{Colors.RESET} Set Dungeon Level")
        print(f"{Colors.YELLOW}4.{Colors.RESET} Teleport to Room")
        print(f"{Colors.YELLOW}5.{Colors.RESET} Spawn Enemies in Current Room")
        print(f"{Colors.YELLOW}6.{Colors.RESET} Instantly Complete a Quest")
        print(f"{Colors.YELLOW}7.{Colors.RESET} Heal Player")
        print(f"{Colors.YELLOW}8.{Colors.RESET} Save Game")
        print(f"{Colors.YELLOW}9.{Colors.RESET} Load Game")
        print(f"{Colors.RED}0. Exit Debug Menu{Colors.RESET}")

        choice = input("\nEnter choice: ")

        if choice == "1":
            try:
                # Give Item
                enemy_type = input(f"{Colors.CYAN}Enter enemy name (Goblin/Sqeleton/Wolf/Orc...): {Colors.RESET}")
                item_type = input(f"{Colors.CYAN}Enter item type (weapon/armor/potion/all): {Colors.RESET}").lower()
                rarity = input(f"{Colors.CYAN}Enter rarity (common/uncommon/rare/epic/legendary/divine/??? or 'random'): {Colors.RESET}").lower()
                item_name = input(f"{Colors.CYAN}Enter specific item name (or 'random' to pick a random one): {Colors.RESET}").title()
                rarity_boost = float(input(f"{Colors.CYAN}Enter rarity boost (1.0 = normal, higher = better items): {Colors.RESET}"))
                level_boost = int(input(f"{Colors.CYAN}Enter rarity boost (level = dungeon_level + level_boost) /!\ HAS TO BE AN INT /!\: {Colors.RESET}"))

                # Convert inputs to proper values
                item_type = None if item_type == "all" else item_type
                rarity = None if rarity == "random" else rarity
                item_name = None if item_name.lower() == "random" else item_name

                # Generate item with specified parameters
                item = generate_random_item(player=player, enemy_type=enemy_type.capitalize(), item_type=item_type, rarity=rarity, item_name=item_name, rarity_boost=rarity_boost, level_boost=level_boost)
            except ValueError as e:
                logger.warning(f"ValueError in give item input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
                handle_error()
                item = None
            except Exception as e:
                logger.warning(f"Exception in give item input: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")
                handle_error()
                item = None
            finally:
                if item:
                    player.inventory.append(item)
                    print(f"{Colors.GREEN}Added item: {item.name}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Failed to generate item! Check your input.{Colors.RESET}")

        elif choice == "2":
            try:
                # Modify Player Stats
                player.stats.permanent_stats["hp"] = int(input(f"{Colors.CYAN}Set HP: {Colors.RESET}") or player.stats["hp"])
                player.stats.permanent_stats["max_hp"] = int(input(f"{Colors.CYAN}Set Max HP: {Colors.RESET}") or player.stats["max_hp"])
                player.stats.permanent_stats["attack"] = int(input(f"{Colors.CYAN}Set Attack: {Colors.RESET}") or player.stats["attack"])
                player.stats.permanent_stats["defense"] = int(input(f"{Colors.CYAN}Set Defense: {Colors.RESET}") or player.stats["defense"])
                player.stats.permanent_stats["luck"] = int(input(f"{Colors.CYAN}Set Luck: {Colors.RESET}") or player.stats["luck"])
                player.xp = int(input(f"{Colors.CYAN}Set XP: {Colors.RESET}") or player.xp)
                player.gold = int(input(f"{Colors.CYAN}Set Gold: {Colors.RESET}") or player.gold)
                for i in range(int(input(f"{Colors.CYAN}Set Level: {Colors.RESET}") or 0)):
                    player.level_up()
                print(f"{Colors.GREEN}Player stats updated!{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in modify player stats input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
                handle_error()
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")
                handle_error()

        elif choice == "3":
            try:
                # Set Dungeon Level
                new_level = int(input(f"{Colors.CYAN}Set new dungeon level: {Colors.RESET}"))
                player.dungeon_level = new_level
                print(f"{Colors.GREEN}Dungeon level set to {new_level}{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in set dungeon level input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
                handle_error()
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")
                handle_error()

        elif choice == "4":
            if input('Generate or Teleport ? (G/T)').upper() == "G":
                try:
                    lvl = int(input('Level room: '))
                except ValueError as e:
                    logger.warning(f"ValueError in teleport input: {e}")
                    print('Invalid input')
                    continue
                except TypeError as e:
                    logger.warning(f"TypeError in teleport input: {e}")
                    print('Invalid input')
                    continue
                rtype = input('Room type ("combat", "treasure", "shop", "rest", "puzzle"): ')
                if rtype not in ["combat", "treasure", "shop", "rest", "puzzle"]:
                    print('Room type not in list, Room Type = None (random room)')
                    rtype = None
                if input('Boss Room (y/n): ') == "y":
                    isboss = True
                else:
                    isboss = False
                dungeon.rooms.insert(generate_random_room(player=player, room_type=rtype, is_boss_room=isboss))
            # Teleport to a Room
            room = dungeon.rooms
            print("rooms:", room)
            room_type = input(f"{Colors.CYAN}Enter room type (combat/shop/treasure/boss/puzzle/trap): {Colors.RESET}")
            if room:
                dungeon.current_room_index
                print(f"{Colors.GREEN}Teleported to {room_type} room.{Colors.RESET}")
            else:
                print(f"{Colors.RED}No room of that type found.{Colors.RESET}")

        elif choice == "5":
            try:
                # Spawn Enemies in Current Room
                num_enemies = int(input(f"{Colors.CYAN}Enter number of enemies to spawn: {Colors.RESET}"))
                for _ in range(num_enemies):
                    # ask for enemy level:
                    enemy_level = int(input(f"{Colors.CYAN}Enter enemy level: {Colors.RESET}"))
                    # ask if enemy a boss:
                    is_boss = input(f"{Colors.CYAN}Is enemy a boss (y/n): {Colors.RESET}")
                    enemy = generate_enemy(enemy_level, is_boss, player)
                    dungeon.rooms.append(enemy)
                    print(f"{Colors.RED}Spawned enemy: {enemy.name}{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in spawn enemies input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")

        elif choice == "6":
            try:
                # Complete a Quest Instantly
                if player.quests:
                    for i, quest in enumerate(player.quests):
                        print(f"{Colors.YELLOW}{i+1}. {quest.title}{Colors.RESET}")
                    quest_choice = int(input(f"{Colors.CYAN}Enter quest number to complete: {Colors.RESET}")) - 1
                    if 0 <= quest_choice < len(player.quests):
                        player.quests[quest_choice].completed = True
                        player.completed_quests.append(player.quests.pop(quest_choice))
                        print(f"{Colors.GREEN}Quest completed!{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}No active quests.{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in complete quest input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")

        elif choice == "7":
            # Heal Player
            player.stats.hp = player.stats.max_hp
            print(f"{Colors.GREEN}Player fully healed!{Colors.RESET}")

        elif choice == "8":
            try:
                # Save Game
                save_name = input(f"{Colors.YELLOW}Enter save name: {Colors.RESET}")
                player.save_player(save_name)
                print(f"{Colors.GREEN}Game saved!{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught during save game: {e}")
                print(f"{Colors.RED}Error saving game: {e}{Colors.RESET}")

        elif choice == "9":
            try:
                # Load Game
                loaded_player = load_player()
                if loaded_player:
                    player = loaded_player
                    print(f"{Colors.GREEN}Game loaded!{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught during load game: {e}")
                print(f"{Colors.RED}Error loading game: {e}{Colors.RESET}")

        elif choice == "0":
            # Exit Debug Menu
            print(f"{Colors.RED}Exiting Debug Menu...{Colors.RESET}")
            break

        else:
            print(f"{Colors.RED}Invalid choice! Try again.{Colors.RESET}")
